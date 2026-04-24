from fastapi import FastAPI
from pydantic import BaseModel
from app.orchestrator.workflow import run_workflow

app = FastAPI(title="SEA Travel Planner")

class TripRequest(BaseModel):
    origin: str
    destinations: list[str]
    budget: float | None = None
    duration_days: int
    travelers: int = 1
    preferences: list[str] = []

def build_raw_request(req: TripRequest) -> str:
    """
    Convert structured API input into a natural language request
    for compatibility with request_parser.
    """

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

    return " ".join(parts)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {
        "message": "SEA Travel Planner API is running.",
        "docs_url": "/docs",
        "health_url": "/health"
    }

@app.post("/plan")
async def plan(req: TripRequest):
    # Convert structured request → natural language string
    raw_request = build_raw_request(req)

    return await run_workflow(raw_request)