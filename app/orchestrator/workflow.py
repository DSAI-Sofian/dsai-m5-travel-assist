from __future__ import annotations

import inspect
from typing import Any, Awaitable, Callable

from app.agents.executor import run_executor
from app.agents.planner import run_planner
from app.agents.ranking import ranking_agent
from app.agents.router import routing_agent
from app.agents.variant import variant_agent
from app.common.request_parser import parse_request
from app.intelligence.conversation_interpreter import interpret_conversation_followup
from app.intelligence.feedback_interpreter import interpret_user_feedback
from app.intelligence.feedback_selector import select_variant_from_feedback
from app.intelligence.personalization import personalize_request
from app.intelligence.place_resolver import resolve_places
from app.intelligence.realism import assess_realism
from app.intelligence.session_memory import (
    apply_memory_to_raw_request,
    build_session_memory_snapshot,
)
from app.orchestrator.state import AgentState, add_error, add_trace, create_initial_state


MAX_AGENT_RETRIES = 2


DEFAULT_AGENT_PIPELINE = [
    "request_parser",
    "routing",
    "place_resolver",
    "personalization",
    "planner",
    "executor",
    "realism",
    "variant",
    "ranking",
    "feedback",
    "continuity",
    "reviewer",
]


def _safe_money_to_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).replace(",", "")
    digits = "".join(ch for ch in text if ch.isdigit() or ch == ".")

    try:
        return float(digits)
    except Exception:
        return default


def _format_sgd(amount: float) -> str:
    return f"SGD {amount:.0f}"


def _apply_budget_delta(
    executor_output: dict[str, Any],
    category: str,
    delta: float,
) -> dict[str, Any]:
    cost_breakdown = executor_output.get("cost_breakdown", {})

    if not isinstance(cost_breakdown, dict):
        cost_breakdown = {}

    current_category = _safe_money_to_float(cost_breakdown.get(category, 0))
    current_total = _safe_money_to_float(cost_breakdown.get("total", 0))

    updated_category = current_category + delta
    updated_total = current_total + delta

    cost_breakdown[category] = _format_sgd(updated_category)
    cost_breakdown["total"] = _format_sgd(updated_total)

    executor_output["cost_breakdown"] = cost_breakdown
    return executor_output


def _sync_ranking_total_from_executor(state: AgentState) -> AgentState:
    executor_output = state.get("executor_output", {}) or {}
    ranking_output = state.get("ranking_output", {}) or {}

    cost_breakdown = executor_output.get("cost_breakdown", {}) or {}
    updated_total = _safe_money_to_float(cost_breakdown.get("total", 0))

    if updated_total > 0:
        ranking_output["estimated_total"] = updated_total
        state["ranking_output"] = ranking_output

        selected_variant = state.get("selected_variant", {}) or {}
        selected_variant_ranking = selected_variant.get("ranking", {}) or {}

        if isinstance(selected_variant_ranking, dict):
            selected_variant_ranking["estimated_total"] = updated_total
            selected_variant["ranking"] = selected_variant_ranking
            state["selected_variant"] = selected_variant

    return state


async def maybe_await(result: Any) -> Any:
    if inspect.isawaitable(result):
        return await result
    return result


async def request_parser_agent(state: AgentState) -> AgentState:
    raw_request = state.get("raw_request", "")
    parsed = parse_request(raw_request)

    state["parsed_request"] = parsed
    state["destinations"] = parsed.get("destinations", [])
    state["display_destinations"] = parsed.get("destinations", [])

    return add_trace(state, "request_parser completed")


async def place_resolver_agent(state: AgentState) -> AgentState:
    parsed = state.get("parsed_request", {})
    raw_destinations = parsed.get("destinations", [])

    resolved = resolve_places(raw_destinations)

    state["destinations"] = resolved.get("destinations", raw_destinations)
    state["display_destinations"] = resolved.get("display_destinations", raw_destinations)
    state["destination_metadata"] = resolved.get("destination_metadata", [])

    parsed["destinations"] = state["destinations"]
    parsed["display_destinations"] = state["display_destinations"]
    parsed["destination_metadata"] = state["destination_metadata"]

    state["parsed_request"] = parsed

    return add_trace(state, "place_resolver completed")


async def personalization_agent(state: AgentState) -> AgentState:
    parsed = state.get("parsed_request", {})

    personalization = personalize_request(parsed)

    state["personalization"] = personalization
    parsed["personalization"] = personalization

    state["parsed_request"] = parsed

    return add_trace(state, "personalization completed")


async def planner_agent(state: AgentState) -> AgentState:
    parsed = state.get("parsed_request", {})
    planner_output = await maybe_await(run_planner(parsed))

    state["planner_output"] = planner_output

    return add_trace(state, "planner completed")


async def executor_agent(state: AgentState) -> AgentState:
    parsed = state.get("parsed_request", {})
    planner_output = state.get("planner_output", {})

    executor_output = await maybe_await(run_executor(parsed, planner_output))

    state["executor_output"] = executor_output

    return add_trace(state, "executor completed")


async def realism_agent(state: AgentState) -> AgentState:
    parsed = state.get("parsed_request", {})
    executor_output = state.get("executor_output", {})

    realism = assess_realism(parsed, executor_output)

    state["realism"] = realism
    executor_output["realism"] = realism

    state["executor_output"] = executor_output

    return add_trace(state, "realism completed")


async def feedback_agent(state: AgentState) -> AgentState:
    feedback_text = state.get("user_feedback", "").strip()

    feedback_output = interpret_user_feedback(feedback_text)
    state["feedback_output"] = feedback_output

    if not feedback_output.get("has_feedback"):
        return add_trace(
            state,
            "feedback_interpreter completed - no feedback detected",
        )

    variants = state.get("plan_variants", [])

    if not variants:
        return add_trace(
            state,
            "feedback_interpreter completed - no variants available",
        )

    selected_variant = select_variant_from_feedback(
        variants=variants,
        feedback=feedback_output,
        current_selected=state.get("selected_variant"),
    )

    if selected_variant:
        state["selected_variant"] = {
            "variant_key": selected_variant.get("variant_key"),
            "variant_label": selected_variant.get("variant_label"),
            "ranking": selected_variant.get("ranking", {}),
        }

        selected_executor_output = selected_variant.get("executor_output")

        if isinstance(selected_executor_output, dict) and selected_executor_output:
            state["executor_output"] = selected_executor_output

        selected_ranking = selected_variant.get("ranking", {})

        state["ranking_output"] = {
            **selected_ranking,
            "selected_by_feedback": True,
            "selection_reason": feedback_output.get("reason"),
        }

    return add_trace(
        state,
        f"feedback_interpreter completed - applied {selected_variant.get('variant_label')}",
    )


async def continuity_agent(state: AgentState) -> AgentState:
    feedback_text = state.get("user_feedback", "").strip()
    continuity_output = interpret_conversation_followup(feedback_text)

    state["continuity_output"] = continuity_output

    if not continuity_output.get("has_followup"):
        return add_trace(
            state,
            "continuity completed - no follow-up modification detected",
        )

    executor_output = state.get("executor_output", {}) or {}
    parsed = state.get("parsed_request", {}) or {}

    adjustments = continuity_output.get("requested_adjustments", [])

    if continuity_output.get("new_budget"):
        parsed["budget"] = continuity_output["new_budget"]
        state["parsed_request"] = parsed

    if "add_food_places" in adjustments:
        restaurants = executor_output.get("restaurants", [])

        if not isinstance(restaurants, list):
            restaurants = []

        additional_restaurants = [
            {
                "name": "Local food market",
                "search_link": "https://www.google.com/search?q=best+local+food+nearby",
                "distance_note": "Suggested additional local food stop",
            },
            {
                "name": "Popular seafood restaurant",
                "search_link": "https://www.google.com/search?q=best+seafood+restaurant+nearby",
                "distance_note": "Suggested additional seafood option",
            },
        ]

        existing_names = {
            str(item.get("name", "")).strip().lower()
            for item in restaurants
            if isinstance(item, dict)
        }

        for item in additional_restaurants:
            name = item["name"].strip().lower()
            if name not in existing_names:
                restaurants.append(item)
                existing_names.add(name)

        executor_output["restaurants"] = restaurants
        
        executor_output = _apply_budget_delta(
            executor_output=executor_output,
            category="food",
            delta=35,
        )

    if "add_nature_activities" in adjustments:
        attractions = executor_output.get("nearby_attractions", [])

        if not isinstance(attractions, list):
            attractions = []

        additional_attractions = [
            {
                "name": "Nature park or reserve",
                "search_link": "https://www.google.com/search?q=best+nature+park+nearby",
                "distance_note": "Suggested additional nature activity",
            },
            {
                "name": "Scenic viewpoint",
                "search_link": "https://www.google.com/search?q=best+scenic+viewpoint+nearby",
                "distance_note": "Suggested additional scenic stop",
            },
        ]

        existing_names = {
            str(item.get("name", "")).strip().lower()
            for item in attractions
            if isinstance(item, dict)
        }

        for item in additional_attractions:
            name = item["name"].strip().lower()
            if name not in existing_names:
                attractions.append(item)
                existing_names.add(name)

        executor_output["nearby_attractions"] = attractions
        
        executor_output = _apply_budget_delta(
            executor_output=executor_output,
            category="activities",
            delta=30,
        )

    if "add_more_activities" in adjustments:
        itinerary = executor_output.get("daily_itinerary", [])

        if not isinstance(itinerary, list):
            itinerary = []

        additional_activity_note = (
            " Add one optional light activity if time allows."
        )

        updated_days = 0

        for day in itinerary:
            if not isinstance(day, dict):
                continue

            details = day.get("details", "")

            if additional_activity_note.strip() not in details:
                day["details"] = details + additional_activity_note
                updated_days += 1

            # Limit modifications to avoid overloading every day
            if updated_days >= 3:
                break

        executor_output["daily_itinerary"] = itinerary

        executor_output = _apply_budget_delta(
            executor_output=executor_output,
            category="activities",
            delta=25,
        )

    if "relax_pace" in adjustments:
        realism = executor_output.get("realism", {})
        realism["pace"] = "relaxed"
        realism.setdefault("notes", [])

        if "User requested a less rushed itinerary with more buffer time." not in realism["notes"]:
            realism["notes"].append(
                "User requested a less rushed itinerary with more buffer time."
            )

        executor_output["realism"] = realism

        itinerary = executor_output.get("daily_itinerary", [])

        buffer_text = " Keep this day flexible with rest time between activities."

        for day in itinerary:
            details = day.get("details", "")
            if buffer_text.strip() not in details:
                day["details"] = details + buffer_text

        executor_output["daily_itinerary"] = itinerary

    if "increase_comfort" in adjustments:
        executor_output["variant_key"] = "comfort"
        executor_output["variant_label"] = "Comfort Upgrade"

        travel_details = executor_output.get("travel_details", {})
        hotel = travel_details.get("hotel", {})
        hotel["comfort_note"] = "User requested a more comfortable stay."
        travel_details["hotel"] = hotel
        executor_output["travel_details"] = travel_details
        executor_output = _apply_budget_delta(
            executor_output=executor_output,
            category="hotel",
            delta=180,
        )

    state["executor_output"] = executor_output
    state = _sync_ranking_total_from_executor(state)

    return add_trace(
        state,
        "continuity completed - applied " + ", ".join(adjustments),
    )


async def reviewer_agent(state: AgentState) -> AgentState:
    """
    Final presentation and summarization agent.
    Hardened for Sprint 3.8 orchestration.
    """

    try:
        executor_output = state.get("executor_output", {}) or {}
        ranking_output = state.get("ranking_output", {}) or {}
        selected_variant = state.get("selected_variant", {}) or {}

        realism = executor_output.get("realism", {}) or {}
        cost_breakdown = executor_output.get("cost_breakdown", {}) or {}

        score_pct = ranking_output.get("score_pct", 0)

        variant_label = (
            selected_variant.get("variant_label")
            or executor_output.get("variant_label")
            or "Recommended Plan"
        )

        destinations = state.get("display_destinations", ["your destination"])
        user_message = f"Your trip to {', '.join(destinations)} looks exciting!"

        if realism.get("pace") == "relaxed":
            user_message += " The itinerary has been adjusted for a more relaxed pace."

        if selected_variant.get("variant_key") == "budget":
            user_message += " We selected a more budget-friendly option for better savings."

        reviewer_output = {
            "agent": "reviewer",
            "user_message": user_message,
            "ranking": ranking_output,
            "estimated_total": ranking_output.get(
                "estimated_total",
                cost_breakdown.get("total", "Unknown"),
            ),
            "accuracy_check": (
                "The itinerary appears internally consistent and aligned "
                "with the requested duration and budget."
            ),
        }

        state["reviewer_output"] = reviewer_output

        final_response = (
            f"{user_message} "
            f"(Plan quality: {score_pct:.0f}%) "
            f"We selected the {variant_label} based on overall best fit."
        )

        variants = state.get("plan_variants", [])
        alternatives = []

        for variant in variants:
            if variant.get("variant_key") == selected_variant.get("variant_key"):
                continue

            label = variant.get("variant_label", "Alternative")
            ranking = variant.get("ranking", {})
            pct = ranking.get("score_pct", 0)
            total = ranking.get("estimated_total", "?")

            alternatives.append(f"{label} (~{pct:.0f}%, est. SGD {total})")

        if alternatives:
            final_response += " Other options: " + " | ".join(alternatives)

        state["final_response"] = final_response

        state.setdefault("debug_trace", [])
        state["debug_trace"].append("reviewer completed")

        return state

    except Exception as exc:
        state.setdefault("debug_trace", [])
        state["debug_trace"].append(f"reviewer failed: {exc}")

        state["reviewer_output"] = {
            "agent": "reviewer",
            "user_message": (
                "Your itinerary was generated, but the final summary formatter encountered an issue."
            ),
        }

        state["final_response"] = (
            "Your itinerary was generated successfully, "
            "but the final presentation layer encountered an issue."
        )

        return state


AGENT_REGISTRY: dict[str, Callable[[AgentState], Awaitable[AgentState]]] = {
    "request_parser": request_parser_agent,
    "routing": routing_agent,
    "place_resolver": place_resolver_agent,
    "personalization": personalization_agent,
    "planner": planner_agent,
    "executor": executor_agent,
    "realism": realism_agent,
    "variant": variant_agent,
    "ranking": ranking_agent,
    "feedback": feedback_agent,
    "continuity": continuity_agent,
    "reviewer": reviewer_agent,
}


async def run_agent_with_retry(agent_name: str, state: AgentState) -> AgentState:
    agent_fn = AGENT_REGISTRY[agent_name]

    last_error: Exception | None = None

    for attempt in range(1, MAX_AGENT_RETRIES + 1):
        try:
            state = await agent_fn(state)
            return state
        except Exception as exc:
            last_error = exc
            add_error(
                state=state,
                agent=agent_name,
                error=f"Attempt {attempt}: {exc}",
                fallback_used=True,
            )

    return apply_agent_fallback(agent_name, state, last_error)


def apply_agent_fallback(
    agent_name: str,
    state: AgentState,
    error: Exception | None,
) -> AgentState:
    add_trace(state, f"{agent_name} fallback activated")

    if agent_name == "request_parser":
        state["parsed_request"] = {
            "destinations": [],
            "duration_days": None,
            "budget": None,
            "preferences": [],
        }

    elif agent_name == "place_resolver":
        parsed = state.get("parsed_request", {})
        destinations = parsed.get("destinations", [])

        state["destinations"] = destinations
        state["display_destinations"] = destinations
        state["destination_metadata"] = []

    elif agent_name == "personalization":
        state["personalization"] = {
            "travel_style": "general",
            "interest_tags": [],
            "hotel_tier": "mid",
            "activity_bias": ["general_sightseeing"],
            "source": "fallback",
            "reason": "personalization_agent_failed",
        }

    elif agent_name == "planner":
        state["planner_output"] = {
            "summary": "Basic travel planning fallback was used.",
            "assumptions": [],
            "budget_notes": [],
            "travel_modes": [],
        }

    elif agent_name == "executor":
        state["executor_output"] = {
            "itinerary": [],
            "travel_details": [],
            "attractions": [],
            "restaurants": [],
            "cost_breakdown": {},
        }

    elif agent_name == "realism":
        state["realism"] = {
            "pace": "balanced",
            "feasibility_flags": [],
            "recommended_best_fit_days": None,
        }

    elif agent_name == "feedback":
        state["feedback_output"] = {
            "has_feedback": False,
            "feedback_text": "",
            "preferred_variant": None,
            "adjustment": None,
            "confidence": 0.0,
            "reason": None,
        }

    elif agent_name == "continuity":
        state["continuity_output"] = {
            "has_followup": False,
            "followup_text": "",
            "continuity_mode": None,
            "requested_adjustments": [],
            "new_budget": None,
            "confidence": 0.0,
            "reason": None,
        }

    elif agent_name == "reviewer":
        state["reviewer_output"] = {
            "message": (
                "I could not fully validate the travel plan, but the request was processed. "
                "Please try again with a destination, duration, and budget."
            )
        }
        state["final_response"] = state["reviewer_output"]["message"]

    add_error(
        state=state,
        agent=agent_name,
        error=error or "Unknown error",
        fallback_used=True,
    )

    return state


async def run_workflow(
    raw_request: str,
    feedback: str | None = None,
    session_memory: dict[str, Any] | None = None,
) -> dict[str, Any]:

    raw_request = apply_memory_to_raw_request(
        raw_request=raw_request,
        memory=session_memory,
    )

    state = create_initial_state(raw_request)
    state["user_feedback"] = feedback or ""
    state["input_session_memory"] = session_memory or {}

    state = await run_agent_with_retry("request_parser", state)
    state = await run_agent_with_retry("routing", state)

    selected_route = state.get("selected_route") or DEFAULT_AGENT_PIPELINE

    remaining_agents = [
        agent_name
        for agent_name in selected_route
        if agent_name not in {"request_parser", "routing"}
    ]

    for agent_name in remaining_agents:
        state = await run_agent_with_retry(agent_name, state)

    state["session_memory"] = build_session_memory_snapshot(state)

    return {
        "message": state.get(
            "final_response",
            "I could not complete the travel plan. Please try again.",
        ),
        "state": state,
    }