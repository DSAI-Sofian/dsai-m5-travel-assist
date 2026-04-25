from __future__ import annotations

import inspect
from typing import Any, Awaitable, Callable

from app.agents.executor import run_executor
from app.agents.planner import run_planner
from app.agents.ranking import ranking_agent
from app.agents.reviewer import run_reviewer
from app.agents.router import routing_agent
from app.agents.variant import variant_agent
from app.common.request_parser import parse_request
from app.intelligence.feedback_interpreter import interpret_user_feedback
from app.intelligence.feedback_selector import select_variant_from_feedback
from app.intelligence.personalization import personalize_request
from app.intelligence.place_resolver import resolve_places
from app.intelligence.realism import assess_realism
from app.intelligence.conversation_interpreter import interpret_conversation_followup
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

        state["executor_output"] = selected_variant.get(
            "executor_output",
            {},
        )

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
    """
    Sprint 3.8 — Conversational Continuity.

    Applies lightweight follow-up modifications to the selected executor output.
    This keeps the system deterministic and avoids unnecessary full regeneration.
    """

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

        restaurants.extend(
            [
                {
                    "name": "Local food market",
                    "search_link": "https://www.google.com/search?q=best+local+food+nearby",
                    "distance_note": "Suggested local food stop",
                },
                {
                    "name": "Popular seafood restaurant",
                    "search_link": "https://www.google.com/search?q=best+seafood+restaurant+nearby",
                    "distance_note": "Suggested seafood option",
                },
            ]
        )

        executor_output["restaurants"] = restaurants

    if "add_nature_activities" in adjustments:
        attractions = executor_output.get("nearby_attractions", [])

        attractions.extend(
            [
                {
                    "name": "Nature park or reserve",
                    "search_link": "https://www.google.com/search?q=best+nature+park+nearby",
                    "distance_note": "Suggested nature activity",
                },
                {
                    "name": "Scenic viewpoint",
                    "search_link": "https://www.google.com/search?q=best+scenic+viewpoint+nearby",
                    "distance_note": "Suggested scenic stop",
                },
            ]
        )

        executor_output["nearby_attractions"] = attractions

    if "add_more_activities" in adjustments:
        itinerary = executor_output.get("daily_itinerary", [])

        if itinerary:
            itinerary[-1]["details"] = (
                itinerary[-1].get("details", "")
                + " Add one optional light activity if time allows."
            )

        executor_output["daily_itinerary"] = itinerary

    if "relax_pace" in adjustments:
        realism = executor_output.get("realism", {})
        realism["pace"] = "relaxed"
        realism.setdefault("notes", [])
        realism["notes"].append(
            "User requested a less rushed itinerary with more buffer time."
        )

        executor_output["realism"] = realism

        itinerary = executor_output.get("daily_itinerary", [])
        for day in itinerary:
            day["details"] = (
                day.get("details", "")
                + " Keep this day flexible with rest time between activities."
            )

        executor_output["daily_itinerary"] = itinerary

    if "increase_comfort" in adjustments:
        executor_output["variant_key"] = "comfort"
        executor_output["variant_label"] = "Comfort Upgrade"

        travel_details = executor_output.get("travel_details", {})
        hotel = travel_details.get("hotel", {})
        hotel["comfort_note"] = "User requested a more comfortable stay."
        travel_details["hotel"] = hotel
        executor_output["travel_details"] = travel_details

    state["executor_output"] = executor_output

    return add_trace(
        state,
        "continuity completed - applied "
        + ", ".join(adjustments),
    )
    

async def reviewer_agent(state: AgentState) -> AgentState:
    parsed = state.get("parsed_request", {})
    planner_output = state.get("planner_output", {})
    executor_output = state.get("executor_output", {})

    reviewer_output = await maybe_await(
        run_reviewer(
            parsed_request=parsed,
            planner_output=planner_output,
            executor_output=executor_output,
        )
    )

    ranking = state.get("ranking_output", {})
    variants = state.get("plan_variants", [])
    selected = state.get("selected_variant", {})

    reviewer_output["ranking"] = ranking
    state["reviewer_output"] = reviewer_output

    score_pct = ranking.get("score_pct")
    selected_key = selected.get("variant_key")

    base_message = (
        reviewer_output.get("message")
        or reviewer_output.get("user_message")
        or "I prepared your travel plan, but the final summary could not be formatted correctly."
    )

    if selected_key == "comfort" and "budget-friendly" in base_message.lower():
        base_message = base_message.replace(
            "budget-friendly adventure",
            "comfortable and well-paced adventure",
        )

    explanation_parts = []

    if selected:
        label = selected.get("variant_label", "selected plan")
        explanation_parts.append(f"We selected the {label} based on overall best fit.")

    feedback_output = state.get("feedback_output", {})
    if feedback_output.get("has_feedback"):
        feedback_reason = feedback_output.get("reason")
        if feedback_reason:
            explanation_parts.append(f"User feedback applied: {feedback_reason}")

    alternatives = [
        variant
        for variant in variants
        if variant.get("variant_key") != selected.get("variant_key")
    ]

    alt_lines = []

    for alt in alternatives[:2]:
        alt_label = alt.get("variant_label")
        alt_score = alt.get("ranking", {}).get("score_pct")
        alt_total = alt.get("ranking", {}).get("estimated_total")

        if not alt_label or not alt_score:
            continue

        if alt_total:
            line = f"{alt_label} (~{int(alt_score)}%, est. SGD {int(alt_total)})"
        else:
            line = f"{alt_label} (~{int(alt_score)}%)"

        alt_lines.append(line)

    if alt_lines:
        explanation_parts.append("Other options: " + " | ".join(alt_lines))

    explanation = ""
    if explanation_parts:
        explanation = " " + " ".join(explanation_parts)

    if score_pct:
        state["final_response"] = (
            f"{base_message} (Plan quality: {int(score_pct)}%){explanation}"
        )
    else:
        state["final_response"] = base_message + explanation

    return add_trace(state, "reviewer completed")


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
            "travel_style": "balanced",
            "interest_tags": [],
            "hotel_tier": "mid",
            "activity_bias": "general",
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
) -> dict[str, Any]:

    state = create_initial_state(raw_request)

    state["user_feedback"] = feedback or ""

    state = await run_agent_with_retry("request_parser", state)
    state = await run_agent_with_retry("routing", state)

    selected_route = state.get("selected_route") or DEFAULT_AGENT_PIPELINE

    remaining_agents = [
        agent_name
        for agent_name in selected_route
        if agent_name not in {"request_parser", "routing", "reviewer"}
    ]

    for agent_name in remaining_agents:
        state = await run_agent_with_retry(agent_name, state)

    return {
        "message": state.get(
            "final_response",
            "I could not complete the travel plan. Please try again.",
        ),
        "state": state,
    }