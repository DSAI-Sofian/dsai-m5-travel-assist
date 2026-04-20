from app.agents.planner import plan_trip
from app.agents.executor import build_itinerary
from app.agents.reviewer import review_options


def run_workflow(req: dict):
    planner = plan_trip(req)
    executor = build_itinerary(req, planner)
    reviewer = review_options(req, planner, executor)
    return {"planner": planner, "executor": executor, "reviewer": reviewer, "top_3_options": reviewer.get("top_3_options", [])}
