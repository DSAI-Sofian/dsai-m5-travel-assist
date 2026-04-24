from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.agents.ranking import build_ranking_score
from app.orchestrator.state import AgentState


VARIANT_RULES = {
    "budget": {
        "label": "Budget Saver",
        "hotel_factor": 0.85,
        "activities_factor": 0.90,
        "pace": "balanced",
    },
    "balanced": {
        "label": "Balanced Pick",
        "hotel_factor": 1.00,
        "activities_factor": 1.00,
        "pace": "balanced",
    },
    "comfort": {
        "label": "Comfort Upgrade",
        "hotel_factor": 1.20,
        "activities_factor": 1.10,
        "pace": "light",
    },
}


def _extract_amount(value: Any) -> float:
    if value is None:
        return 0.0

    text = str(value).replace(",", "")
    digits = "".join(ch for ch in text if ch.isdigit() or ch == ".")

    try:
        return float(digits)
    except Exception:
        return 0.0


def _format_sgd(amount: float) -> str:
    return f"SGD {amount:.0f}"


def _variant_executor_output(
    base_executor: dict[str, Any],
    variant_key: str,
    rule: dict[str, Any],
) -> dict[str, Any]:
    output = deepcopy(base_executor)

    cost_breakdown = output.get("cost_breakdown", {}).copy()

    hotel = _extract_amount(cost_breakdown.get("hotel"))
    activities = _extract_amount(cost_breakdown.get("activities"))
    flight = _extract_amount(cost_breakdown.get("flight"))
    local_transport = _extract_amount(cost_breakdown.get("local_transport"))
    food = _extract_amount(cost_breakdown.get("food"))

    hotel = hotel * rule["hotel_factor"]
    activities = activities * rule["activities_factor"]

    total = flight + hotel + activities + local_transport + food

    cost_breakdown["hotel"] = _format_sgd(hotel)
    cost_breakdown["activities"] = _format_sgd(activities)
    cost_breakdown["total"] = _format_sgd(total)

    output["cost_breakdown"] = cost_breakdown
    output["variant_key"] = variant_key
    output["variant_label"] = rule["label"]

    output.setdefault("realism", {})
    output["realism"]["pace"] = rule["pace"]

    return output


def build_plan_variants(state: AgentState) -> list[dict[str, Any]]:
    base_executor = state.get("executor_output", {})
    base_realism = state.get("realism", {})

    variants = []

    for variant_key, rule in VARIANT_RULES.items():
        variant_executor = _variant_executor_output(
            base_executor=base_executor,
            variant_key=variant_key,
            rule=rule,
        )

        variant_state = deepcopy(state)
        variant_state["executor_output"] = variant_executor

        variant_realism = {
            **base_realism,
            "pace": rule["pace"],
        }

        base_flags = list(base_realism.get("flags", []))

        if variant_key == "budget":
            variant_realism["flags"] = base_flags + ["lower_comfort"]

        elif variant_key == "comfort":
            variant_realism["flags"] = [
                flag
                for flag in base_flags
                if flag != "too_few_activities_for_duration"
            ]

        else:
            variant_realism["flags"] = base_flags

        variant_state["realism"] = variant_realism
        variant_executor["realism"] = variant_realism

        ranking = build_ranking_score(variant_state)

        variants.append(
            {
                "variant_key": variant_key,
                "variant_label": rule["label"],
                "executor_output": variant_executor,
                "ranking": ranking,
            }
        )

    variants.sort(
        key=lambda item: item["ranking"]["score"],
        reverse=True,
    )

    return variants


async def variant_agent(state: AgentState) -> AgentState:
    variants = build_plan_variants(state)

    best_variant = variants[0] if variants else None

    state["plan_variants"] = variants

    if best_variant:
        state["selected_variant"] = {
            "variant_key": best_variant["variant_key"],
            "variant_label": best_variant["variant_label"],
            "ranking": best_variant["ranking"],
        }

        state["executor_output"] = best_variant["executor_output"]
        state["ranking_output"] = best_variant["ranking"]

        # Ensure realism stays consistent with selected variant
        state["realism"] = best_variant["executor_output"].get("realism", state.get("realism"))

        state.setdefault("debug_trace", [])
        state["debug_trace"].append(
            "variant completed: selected "
            + best_variant["variant_label"]
            + f" | {best_variant['ranking']['score_pct']}%"
        )
    else:
        state.setdefault("debug_trace", [])
        state["debug_trace"].append("variant completed: no variants generated")

    return state