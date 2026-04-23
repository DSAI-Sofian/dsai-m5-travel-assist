from typing import Any, Mapping


_PLANNER_RULES = [
    "Return ONLY JSON",
    "Keep the trip scope tightly aligned to the user's requested destination(s)",
    "Do NOT introduce extra cities, regions, or countries unless the user explicitly asks for them",
    "If the user mentions only one destination, keep the trip focused on that destination only",
    "If the user mentions multiple destinations, you may plan across those destinations only",
    "Do NOT assume cross-border travel unless clearly requested",
    "Travel modes should be realistic for the requested destination(s)",
    "Budget notes should reflect the user's stated budget",
]


def build_planner_constraints():
    """
    Return hard planner constraints.

    This intentionally preserves the current planner constraint set and does not
    introduce new business logic.
    """
    _ = intent
    return list(_PLANNER_RULES)


def format_constraints_for_prompt(constraints: list[str]) -> str:
    """
    Format planner constraints into the existing prompt bullet style.
    """
    return "\n".join(f"- {rule}" for rule in constraints)
