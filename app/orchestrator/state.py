from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class AgentError(TypedDict, total=False):
    agent: str
    error: str
    fallback_used: bool


class AgentState(TypedDict, total=False):
    raw_request: str
    parsed_request: Dict[str, Any]

    selected_route: List[str]
    route_reason: str

    destinations: List[str]
    display_destinations: List[str]
    destination_metadata: List[Dict[str, Any]]

    intent: Dict[str, Any]
    constraints: Dict[str, Any]
    personalization: Dict[str, Any]
    realism: Dict[str, Any]

    plan_variants: List[Dict[str, Any]]
    selected_variant: Dict[str, Any]
    ranking_output: Dict[str, Any]

    planner_output: Dict[str, Any]
    executor_output: Dict[str, Any]
    reviewer_output: Dict[str, Any]

    final_response: str

    errors: List[AgentError]
    debug_trace: List[str]


def create_initial_state(raw_request: str) -> AgentState:
    return {
        "raw_request": raw_request,
        "errors": [],
        "debug_trace": [],
    }


def add_trace(state: AgentState, message: str) -> AgentState:
    state.setdefault("debug_trace", [])
    state["debug_trace"].append(message)
    return state


def add_error(
    state: AgentState,
    agent: str,
    error: Exception | str,
    fallback_used: bool = True,
) -> AgentState:
    state.setdefault("errors", [])
    state["errors"].append(
        {
            "agent": agent,
            "error": str(error),
            "fallback_used": fallback_used,
        }
    )
    return state


def get_nested(state: AgentState, key: str, default: Optional[Any] = None) -> Any:
    return state.get(key, default)