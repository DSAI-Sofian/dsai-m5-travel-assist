# AGENT.md — Travel Assist Bot (Multi-Agent System)

## 1. Purpose

This repository contains a multi-agent AI Travel Assist Bot designed to generate:
- structured travel plans
- cost-aware itineraries
- actionable booking/search links

The system prioritizes:
- correctness over creativity
- realism over generic outputs
- safe and stable execution

---

## 2. Core Architecture

Pipeline:

User (Telegram)
→ Telegram Bot (FastAPI + PTB)
→ Orchestrator (workflow.py)
→ Multi-Agent Pipeline
→ Structured Response

Current agents:
- planner
- executor
- reviewer

Target (upgrade):
- ~12–14 modular agents

---

## 3. Upgrade Objectives (MANDATORY CHECK BEFORE ANY CHANGE)

Every code change MUST be validated against:

### 3.1 Travel Intelligence
- Correct city/airport mapping
- No destination drift
- Region-aware planning

### 3.2 Realism
- Reasonable pricing (not random)
- Travel time feasibility
- Logical itineraries

### 3.3 Personalization
- traveler type (solo, couple, family)
- travel style (budget, food, luxury, adventure)

### 3.4 Reliability
- retry logic for LLM calls
- safe fallback responses
- no pipeline crashes

### 3.5 Link Safety (CRITICAL — DO NOT BREAK)
- Flights → Google Flights search URLs ONLY
- Hotels → Booking.com search URLs ONLY
- Attractions → Google search links ONLY
- NEVER generate deep links

---

## 4. Coding Principles

### 4.1 Incremental Changes Only
- DO NOT rewrite entire system
- Extend existing behavior safely
- Maintain backward compatibility

### 4.2 One Responsibility Per File
Each agent/file should do ONE thing:
- intent interpretation
- constraint handling
- pricing
- itinerary generation
- validation

### 4.3 Deterministic Where Possible
- cost calculation must be deterministic
- reviewer must not recompute differently

### 4.4 Keep Functions Small
- < 100 lines preferred
- split logic into helpers

---

## 5. Agent Design Rules

### 5.1 Stateless by Default
- no hidden global state
- inputs → outputs clearly defined

### 5.2 Structured Outputs Only
Agents must return structured dictionaries, not free text.

Example:
```python
{
  "destination": "Kota Kinabalu",
  "days": 3,
  "budget": 1500,
  "itinerary": [...]
}
```

---

## 6A. Pipeline Data Contract (MANDATORY)

Each agent must:

Input:
- receive a structured dictionary ONLY

Output:
- return a structured dictionary ONLY
- must NOT return raw text

Required minimum fields:
- destination
- duration_days
- budget_sgd

Optional fields:
- traveler_type
- travel_style
- itinerary
- cost_breakdown

Agents MUST NOT:
- remove required fields
- overwrite unrelated fields
- change data types

Violation of this contract will break downstream agents.

---

## 6B. Agent Execution Rules

- Agents are executed strictly in pipeline order
- No agent should call another agent directly
- All coordination happens ONLY through orchestrator

Future pipeline example:
parser → intent → constraint → destination → itinerary → pricing → validation → summary

---

## 7A. Failure Output Contract

If an agent fails after retries:

System must return:
{
  "status": "fallback",
  "message": "Unable to generate full plan, showing best available result.",
  "partial_data": {...}
}

Rules:
- Never return empty response
- Never expose internal errors to user
- Always preserve safe links if already generated

---

## 17. Definition of Done

A feature/change is considered complete only if:

- passes manual regression checks
- does not break Telegram output
- maintains cost correctness
- preserves link safety
- improves realism or reliability

If not, it is incomplete.