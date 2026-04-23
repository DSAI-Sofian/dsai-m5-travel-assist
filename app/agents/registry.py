from typing import Any, Callable, Mapping
from types import MappingProxyType

AgentHandler = Callable[[dict[str, Any]], dict[str, Any]]

_REGISTRY: dict[str, AgentHandler] | None = None


def _build_registry() -> dict[str, AgentHandler]:
    from app.agents.executor import build_itinerary
    from app.agents.planner import plan_trip
    from app.agents.reviewer import review_options

    return {
        "planner": plan_trip,
        "executor": build_itinerary,
        "reviewer": review_options,
    }


def get_agent_registry() -> Mapping[str, AgentHandler]:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = _build_registry()
    return MappingProxyType(_REGISTRY)


def get_agent_handler(name: str) -> AgentHandler:
    registry = get_agent_registry()
    try:
        return registry[name]
    except KeyError as exc:
        supported = ", ".join(sorted(registry.keys()))
        raise KeyError(
            f"Unknown agent '{name}'. Supported agents: {supported}"
        ) from exc