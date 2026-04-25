from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator

from app.orchestrator.workflow import run_workflow


app = FastAPI(title="SEA Travel Planner")


class TripRequest(BaseModel):
    origin: str = Field(default="Singapore", min_length=1)
    destinations: list[str] = Field(default_factory=list)
    budget: float | None = Field(default=None, ge=0)
    duration_days: int = Field(default=4, ge=1, le=30)
    travelers: int = Field(default=1, ge=1, le=20)
    preferences: list[str] = Field(default_factory=list)
    feedback: str | None = None
    session_memory: dict[str, Any] | None = None
    include_state: bool = False

    @field_validator("destinations", "preferences")
    @classmethod
    def clean_string_lists(cls, value: list[str]) -> list[str]:
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    @field_validator("feedback")
    @classmethod
    def clean_feedback(cls, value: str | None) -> str | None:
        if value is None:
            return None

        cleaned = value.strip()
        return cleaned or None


def build_raw_request(req: TripRequest) -> str:
    parts: list[str] = []

    if req.duration_days:
        parts.append(f"{req.duration_days} days")

    if req.destinations:
        parts.append(" ".join(req.destinations))

    if req.budget is not None:
        parts.append(f"budget S${int(req.budget)}")

    if req.preferences:
        parts.append(" ".join(req.preferences))

    if req.travelers > 1:
        parts.append(f"for {req.travelers} people")

    if req.feedback:
        parts.append(f"feedback: {req.feedback}")

    return " ".join(parts).strip()


def build_demo_response(
    workflow_result: dict[str, Any],
    include_state: bool = False,
) -> dict[str, Any]:
    state = workflow_result.get("state", {}) or {}

    parsed_request = state.get("parsed_request", {}) or {}
    executor_output = state.get("executor_output", {}) or {}
    reviewer_output = state.get("reviewer_output", {}) or {}
    ranking_output = state.get("ranking_output", {}) or {}
    selected_variant = state.get("selected_variant", {}) or {}
    feedback_output = state.get("feedback_output", {}) or {}
    continuity_output = state.get("continuity_output", {}) or {}
    session_memory = state.get("session_memory", {}) or {}
    variants = state.get("plan_variants", []) or []
    errors = state.get("errors", []) or []

    response = {
        "message": workflow_result.get("message"),
        "request": {
            **parsed_request,
            "display_destinations": state.get("display_destinations", []),
        },
        "executor": executor_output,
        "reviewer": reviewer_output,
        "ranking": ranking_output,
        "selected_variant": selected_variant,
        "variants": [
            {
                "variant_key": v.get("variant_key"),
                "variant_label": v.get("variant_label"),
                "ranking": v.get("ranking", {}),
            }
            for v in variants
        ],
        "feedback": feedback_output,
        "continuity": continuity_output,
        "session_memory": session_memory,
        "debug_trace": state.get("debug_trace", []),
        "errors": errors,
        "status": "ok" if not errors else "completed_with_warnings",
    }

    if include_state:
        response["state"] = state

    return response


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {
        "message": "SEA Travel Planner API is running.",
        "docs_url": "/docs",
        "health_url": "/health",
    }


@app.post("/plan")
async def plan(req: TripRequest):
    raw_request = build_raw_request(req)

    try:
        workflow_result = await run_workflow(
            raw_request=raw_request,
            feedback=req.feedback,
            session_memory=req.session_memory,
        )

        return build_demo_response(
            workflow_result=workflow_result,
            include_state=req.include_state,
        )

    except Exception as exc:
        return {
            "status": "error",
            "message": (
                "I could not complete the travel plan due to a system error. "
                "Please try again with destination, duration, budget, and preferences."
            ),
            "error_type": exc.__class__.__name__,
            "debug_trace": [],
            "errors": [str(exc)],
        }