from copy import deepcopy
from app.agents.planner import plan_trip
from app.agents.executor import build_itinerary
from app.agents.reviewer import review_options
from app.common.destination_normalizer import normalize_destinations


def run_workflow(req: dict):
    normalized_req = deepcopy(req)

    destinations = normalized_req.get("destinations", [])
    normalized_req["destinations"] = normalize_destinations(destinations)

    planner = plan_trip(normalized_req)
    executor = build_itinerary(normalized_req, planner)
    reviewer = review_options(normalized_req, planner, executor)

    return {
        "request": normalized_req,
        "planner": planner,
        "executor": executor,
        "reviewer": reviewer,
        "top_3_options": reviewer.get("top_3_options", []),
    }