from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any

from app.orchestrator.workflow import run_workflow


app = FastAPI(title="SEA Travel Planner")


class TripRequest(BaseModel):
    origin: str
    destinations: list[str]
    budget: float | None = None
    duration_days: int
    travelers: int = 1
    preferences: list[str] = []
    feedback: str | None = None
    session_memory: dict[str, Any] | None = None


def build_raw_request(req: TripRequest) -> str:
    parts = []

    if req.duration_days:
        parts.append(f"{req.duration_days} days")

    if req.destinations:
        parts.append(" ".join(req.destinations))

    if req.budget:
        parts.append(f"budget S${int(req.budget)}")

    if req.preferences:
        parts.append(" ".join(req.preferences))

    if req.travelers > 1:
        parts.append(f"for {req.travelers} people")

    if req.feedback:
        parts.append(f"feedback: {req.feedback}")

    return " ".join(parts)


def build_demo_response(workflow_result: dict[str, Any]) -> dict[str, Any]:
    state = workflow_result.get("state", {}) or {}

    parsed_request = state.get("parsed_request", {}) or {}
    executor_output = state.get("executor_output", {}) or {}
    reviewer_output = state.get("reviewer_output", {}) or {}
    ranking_output = state.get("ranking_output", {}) or {}
    selected_variant = state.get("selected_variant", {}) or {}
    feedback_output = state.get("feedback_output", {}) or {}
    continuity_output = state.get("continuity_output", {}) or {}
    session_memory = state.get("session_memory", {}) or {}

    return {
        "message": workflow_result.get("message"),
        "request": {
            **parsed_request,
            "display_destinations": state.get("display_destinations", []),
        },
        "executor": executor_output,
        "reviewer": reviewer_output,
        "ranking": ranking_output,
        "selected_variant": selected_variant,
        "feedback": feedback_output,
        "continuity": continuity_output,
        "session_memory": session_memory,
        "debug_trace": state.get("debug_trace", []),
        "errors": state.get("errors", []),
        "state": state,
    }


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

    workflow_result = await run_workflow(
        raw_request=raw_request,
        feedback=req.feedback,
        session_memory=req.session_memory,
    )

    return build_demo_response(workflow_result)