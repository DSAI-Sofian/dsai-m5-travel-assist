from __future__ import annotations

import re
from typing import Any

from app.orchestrator.state import AgentState


def _extract_amount(value: Any) -> float | None:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value)
    match = re.search(r"(\d+(?:\.\d+)?)", text.replace(",", ""))

    if not match:
        return None

    return float(match.group(1))


def _score_budget_fit(budget: float | None, total: float | None) -> float:
    if budget is None or total is None:
        return 0.6

    if total <= budget:
        return 1.0

    over_ratio = (total - budget) / budget

    if over_ratio <= 0.1:
        return 0.8
    if over_ratio <= 0.25:
        return 0.5

    return 0.2


def _score_realism(realism: dict[str, Any]) -> float:
    if not realism:
        return 0.6

    feasible = realism.get("feasible", True)
    flags = realism.get("flags") or []

    if not feasible:
        return 0.3

    if len(flags) == 0:
        return 1.0

    if len(flags) <= 2:
        return 0.75

    return 0.5


def _score_preference_fit(parsed_request: dict[str, Any], executor_output: dict[str, Any]) -> float:
    preferences = parsed_request.get("preferences") or []

    if not preferences:
        return 0.7

    combined_text = str(executor_output).lower()

    matched = 0
    for pref in preferences:
        pref_text = str(pref).lower()
        tokens = [t for t in pref_text.split() if t not in {"budget", "s", "sgd"}]

        if any(token in combined_text for token in tokens):
            matched += 1

    if matched == 0:
        return 0.4

    return min(1.0, matched / max(1, len(preferences)))


def _score_destination_confidence(state: AgentState) -> float:
    metadata = state.get("destination_metadata") or []
    destinations = state.get("destinations") or []

    if metadata:
        return 1.0

    if destinations:
        return 0.75

    return 0.3


def build_ranking_score(state: AgentState) -> dict[str, Any]:
    parsed_request = state.get("parsed_request", {})
    executor_output = state.get("executor_output", {})
    realism = state.get("realism", {})

    budget = _extract_amount(parsed_request.get("budget"))
    total = _extract_amount(
        executor_output.get("cost_breakdown", {}).get("total")
    )

    budget_score = _score_budget_fit(budget, total)
    realism_score = _score_realism(realism)
    preference_score = _score_preference_fit(parsed_request, executor_output)
    destination_score = _score_destination_confidence(state)

    final_score = (
        0.40 * budget_score
        + 0.25 * realism_score
        + 0.20 * preference_score
        + 0.15 * destination_score
    )

    return {
        "agent": "ranking",
        "score": round(final_score, 3),
        "score_pct": round(final_score * 100, 1),
        "components": {
            "budget_fit": round(budget_score, 3),
            "realism_fit": round(realism_score, 3),
            "preference_fit": round(preference_score, 3),
            "destination_confidence": round(destination_score, 3),
        },
        "estimated_total": total,
        "budget": budget,
        "recommendation": _build_recommendation(final_score),
    }


def _build_recommendation(score: float) -> str:
    if score >= 0.85:
        return "strong_fit"
    if score >= 0.70:
        return "good_fit"
    if score >= 0.50:
        return "acceptable_fit"

    return "weak_fit"


async def ranking_agent(state: AgentState) -> AgentState:
    if state.get("selected_variant") and state.get("ranking_output"):
        ranking = state["ranking_output"]
    else:
        ranking = build_ranking_score(state)
        state["ranking_output"] = ranking

    state["ranking_output"] = ranking
    state.setdefault("debug_trace", [])
    state["debug_trace"].append(
        f"ranking completed: {ranking['score_pct']}% | {ranking['recommendation']}"
    )

    return state