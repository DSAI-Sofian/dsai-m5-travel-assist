from __future__ import annotations

from types import MappingProxyType
from typing import Any, Awaitable, Callable, Mapping

from app.orchestrator.state import AgentState


LegacyAgentHandler = Callable[[dict[str, Any]], dict[str, Any]]
WorkflowAgentHandler = Callable[[AgentState], Awaitable[AgentState]]


_LEGACY_REGISTRY: dict[str, LegacyAgentHandler] | None = None
_WORKFLOW_REGISTRY: dict[str, WorkflowAgentHandler] = {}


def _build_legacy_registry() -> dict[str, LegacyAgentHandler]:
    """
    Backward-compatible registry for the original Day 1/2 agent functions.

    Keep this so older imports/tests that call:
        get_agent_registry()
        get_agent_handler(name)

    do not break.
    """
    from app.agents.executor import build_itinerary
    from app.agents.planner import plan_trip
    from app.agents.reviewer import review_options

    return {
        "planner": plan_trip,
        "executor": build_itinerary,
        "reviewer": review_options,
    }


def get_agent_registry() -> Mapping[str, LegacyAgentHandler]:
    """
    Backward-compatible getter for legacy agent handlers.
    """
    global _LEGACY_REGISTRY

    if _LEGACY_REGISTRY is None:
        _LEGACY_REGISTRY = _build_legacy_registry()

    return MappingProxyType(_LEGACY_REGISTRY)


def get_agent_handler(name: str) -> LegacyAgentHandler:
    """
    Backward-compatible getter for legacy agent handlers.
    """
    registry = get_agent_registry()

    try:
        return registry[name]
    except KeyError as exc:
        supported = ", ".join(sorted(registry.keys()))
        raise KeyError(
            f"Unknown legacy agent '{name}'. Supported agents: {supported}"
        ) from exc


def register_workflow_agent(name: str, handler: WorkflowAgentHandler) -> None:
    """
    Register a Day 3 AgentState-based async workflow agent.
    """
    if not name:
        raise ValueError("Workflow agent name cannot be empty.")

    if name in _WORKFLOW_REGISTRY:
        raise ValueError(f"Workflow agent already registered: {name}")

    _WORKFLOW_REGISTRY[name] = handler


def get_workflow_agent_registry() -> Mapping[str, WorkflowAgentHandler]:
    """
    Return registered Day 3 workflow agents.
    """
    return MappingProxyType(_WORKFLOW_REGISTRY)


def get_workflow_agent_handler(name: str) -> WorkflowAgentHandler:
    """
    Retrieve a Day 3 workflow agent by name.
    """
    try:
        return _WORKFLOW_REGISTRY[name]
    except KeyError as exc:
        supported = ", ".join(sorted(_WORKFLOW_REGISTRY.keys())) or "none"
        raise KeyError(
            f"Unknown workflow agent '{name}'. Supported agents: {supported}"
        ) from exc


def clear_workflow_registry() -> None:
    """
    Useful for tests.
    """
    _WORKFLOW_REGISTRY.clear()