from __future__ import annotations

from app.orchestrator.state import AgentState


FULL_TRIP_PIPELINE = [
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

BASIC_TRIP_PIPELINE = [
    "request_parser",
    "routing",
    "place_resolver",
    "planner",
    "executor",
    "realism",
    "variant",
    "ranking",
    "feedback",
    "continuity",
    "reviewer",
]

BUDGET_ONLY_PIPELINE = [
    "request_parser",
    "routing",
    "place_resolver",
    "personalization",
    "planner",
    "executor",
    "variant",
    "ranking",
    "feedback",
    "continuity",
    "reviewer",
]


def _has_preferences(state: AgentState) -> bool:
    parsed = state.get("parsed_request", {})
    preferences = parsed.get("preferences") or []

    noise_tokens = {"budget", "s", "sgd"}

    cleaned = []

    for p in preferences:
        tokens = p.lower().split()
        meaningful = [t for t in tokens if t not in noise_tokens]

        if meaningful:
            cleaned.append(meaningful)

    return len(cleaned) > 0


def _is_budget_only_request(raw_request: str) -> bool:
    budget_keywords = [
        "budget",
        "cost",
        "price",
        "estimate",
        "how much",
        "afford",
    ]

    itinerary_keywords = [
        "itinerary",
        "plan",
        "days",
        "trip",
        "travel",
        "things to do",
        "attractions",
    ]

    has_budget_keyword = any(keyword in raw_request for keyword in budget_keywords)
    has_itinerary_keyword = any(keyword in raw_request for keyword in itinerary_keywords)

    return has_budget_keyword and not has_itinerary_keyword


def build_agent_route(state: AgentState) -> list[str]:
    """
    Lightweight deterministic router.

    Rules:
    1. Budget-only request -> budget-focused route.
    2. No preferences -> skip personalization.
    3. Otherwise -> full trip pipeline.
    """

    raw_request = str(state.get("raw_request", "")).lower()

    if _is_budget_only_request(raw_request):
        state["route_reason"] = "budget_only_request"
        return BUDGET_ONLY_PIPELINE

    if not _has_preferences(state):
        state["route_reason"] = "no_preferences_detected"
        return BASIC_TRIP_PIPELINE

    state["route_reason"] = "full_trip_request"
    return FULL_TRIP_PIPELINE


async def routing_agent(state: AgentState) -> AgentState:
    selected_route = build_agent_route(state)

    state["selected_route"] = selected_route
    state.setdefault("debug_trace", [])
    state["debug_trace"].append(
        "routing completed: "
        + state.get("route_reason", "unknown")
        + " | "
        + " → ".join(selected_route)
    )

    return state