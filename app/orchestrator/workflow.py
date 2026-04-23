from copy import deepcopy
from typing import Any

from app.agents.registry import get_agent_handler
from app.common.destination_normalizer import normalize_destinations
from app.common.guardrails import execute_with_retry

AGENT_PIPELINE = ("planner", "executor", "reviewer")


def _build_failure_response(
    normalized_req: dict[str, Any],
    stage_outputs: dict[str, dict[str, Any]],
    failed_stage: str,
) -> dict[str, Any]:
    reviewer = stage_outputs.get("reviewer", {})
    if not isinstance(reviewer, dict):
        reviewer = {}

    top_3 = reviewer.get("top_3_options", [])
    if not isinstance(top_3, list):
        top_3 = []

    return {
        "status": "fallback",
        "message": "Unable to generate full plan, showing best available result.",
        "failed_stage": failed_stage,
        "request": normalized_req,
        "planner": stage_outputs.get("planner", {}),
        "executor": stage_outputs.get("executor", {}),
        "reviewer": reviewer,
        "top_3_options": top_3,
    }


def run_workflow(req: dict[str, Any]) -> dict[str, Any]:
    normalized_req = deepcopy(req)

    destinations = normalized_req.get("destinations", [])
    if isinstance(destinations, str):
        destinations = [destinations]
    elif not isinstance(destinations, list):
        destinations = []

    # Preserve invariant: destination normalization happens before planner.
    normalized_req["destinations"] = normalize_destinations(destinations)

    stage_outputs: dict[str, dict[str, Any]] = {
        "planner": {},
        "executor": {},
        "reviewer": {},
    }

    for stage_name in AGENT_PIPELINE:
        handler = get_agent_handler(stage_name)

        try:
            if stage_name == "planner":
                result = execute_with_retry(handler, normalized_req)

            elif stage_name == "executor":
                result = execute_with_retry(
                    handler,
                    normalized_req,
                    stage_outputs["planner"],
                )

            elif stage_name == "reviewer":
                result = execute_with_retry(
                    handler,
                    normalized_req,
                    stage_outputs["planner"],
                    stage_outputs["executor"],
                )

            else:
                return _build_failure_response(
                    normalized_req=normalized_req,
                    stage_outputs=stage_outputs,
                    failed_stage=stage_name,
                )

        except Exception:
            # Safe logging only
            print(f"[workflow] stage={stage_name} failed")

            return _build_failure_response(
                normalized_req=normalized_req,
                stage_outputs=stage_outputs,
                failed_stage=stage_name,
            )

        if not isinstance(result, dict):
            print(f"[workflow] stage={stage_name} returned non-dict output")

            return _build_failure_response(
                normalized_req=normalized_req,
                stage_outputs=stage_outputs,
                failed_stage=stage_name,
            )
        
        stage_outputs[stage_name] = result
        
    reviewer = stage_outputs["reviewer"]
    return {
        "request": normalized_req,
        "planner": stage_outputs["planner"],
        "executor": stage_outputs["executor"],
        "reviewer": reviewer,
        "top_3_options": reviewer.get("top_3_options", []),
    }