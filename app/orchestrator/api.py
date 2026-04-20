from fastapi import FastAPI
from pydantic import BaseModel
from app.orchestrator.workflow import run_workflow

app = FastAPI(title="SEA Travel Planner")

class TripRequest(BaseModel):
    origin: str
    destinations: list[str]
    budget: float
    duration_days: int
    travelers: int = 1
    preferences: list[str] = []

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/plan")
def plan(req: TripRequest):
    return run_workflow(req.model_dump())
