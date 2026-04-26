# 🌏 SEA Travel Planner — Multi-Agent AI Travel Assistant

> Project documentation and architecture evolution.

---

# 📌 Overview

SEA Travel Planner is a multi-agent AI-powered travel assistant designed to generate practical, budget-aware travel itineraries for Southeast Asia.

Unlike conventional chatbot-style travel assistants that provide generic recommendations, this system focuses on:

* structured outputs
* deterministic scoring
* explainable orchestration
* realism-aware planning
* budget validation
* conversational continuity

The platform evolved from a simple 3-agent architecture into a modular orchestration framework capable of adaptive travel planning, lightweight memory, and explainable decision-making.

## ⚖️ Usage & Intellectual Property Notice

This repository is published for portfolio and educational review purposes only.

No permission is granted to copy, redistribute, modify, commercialize, or reuse the contents of this repository without explicit written permission from the author.

## 🔒 Lightweight Abuse Protection

The Telegram bot includes a lightweight abuse guard that runs before travel planning begins.

It provides:

- user-level rate limiting
- irrelevant request filtering
- temporary user blocking
- admin alert support through private environment variables

No secrets, user logs, admin chat IDs, or production credentials are stored in the repository.
Runtime values are configured through environment variables in Render.

---

# 🚀 Key Capabilities

## ✅ Core Features

* Natural language travel planning
* Telegram chatbot interface
* Budget-aware itinerary generation
* SGD-normalized cost estimation
* Multi-agent orchestration
* Deterministic ranking engine
* Travel realism assessment
* Conversational continuity
* Lightweight session memory
* Explainability scoring
* Structured JSON contracts
* Debug-state visibility
* Lightweight public abuse guard

---

# 🧠 Architecture Overview

## Current Orchestration Pipeline

```
User Request
→ abuse_guard
→ request_parser
→ routing
→ place_resolver
→ personalization
→ planner
→ executor
→ realism
→ variant
→ ranking
→ feedback
→ continuity
→ session_memory
→ reviewer
```

---

# ⚙️ Multi-Agent Responsibilities

| Agent                | Responsibility                                                       | Guardrails                      |
| -------------------- | -------------------------------------------------------------------- | ------------------------------- |
| Abuse Guard          | Pre-Orchestration defensive gateway that validates incoming requests | Context filtering               |
| Request Parser       | Extracts destination, duration, budget, preferences                  | Parser hygiene filtering        |
| Routing Agent        | Determines active orchestration path                                 | Conditional execution           |
| Place Resolver       | Maps destinations and gateways                                       | Prevents destination drift      |
| Personalization      | Infers travel style and preferences                                  | Controlled preference injection |
| Planner              | Generates structured planning assumptions                            | Scope control                   |
| Executor             | Produces itinerary and travel details                                | Structured JSON outputs         |
| Realism              | Evaluates pacing and feasibility                                     | Avoids unrealistic itineraries  |
| Variant Engine       | Creates multiple plan variants                                       | Deterministic transformations   |
| Ranking Engine       | Scores and selects best variant                                      | Weighted explainable scoring    |
| Feedback Interpreter | Applies user follow-up intent                                        | Controlled mutation             |
| Continuity Layer     | Maintains conversational coherence                                   | Context isolation               |
| Session Memory       | Reuses lightweight preferences                                       | Memory leakage filtering        |
| Reviewer             | Final validation and tone refinement                                 | Budget and consistency checks   |

---

# 📊 Deterministic Ranking System

The system uses weighted deterministic scoring rather than relying solely on LLM-generated recommendations.

## Current Scoring Weights

| Component              | Weight |
| ---------------------- | ------ |
| Budget Fit             | 40%    |
| Realism Fit            | 25%    |
| Preference Match       | 20%    |
| Destination Confidence | 15%    |

---

# 🎯 Variant Engine

The platform generates multiple travel variants automatically:

| Variant         | Goal                               |
| --------------- | ---------------------------------- |
| Budget Saver    | Lowest-cost viable itinerary       |
| Balanced Pick   | Balanced comfort and affordability |
| Comfort Upgrade | Higher-comfort optimized plan      |

Each variant is independently:

* realism-adjusted
* cost-adjusted
* scored
* ranked
* explainable

---

# 🧩 Explainability Features

The system prioritizes explainability across all orchestration stages.

## Responses Include

* selected variant explanation
* plan quality score
* estimated costs
* alternative recommendations
* realism assessment
* orchestration debug traces (optional)

Example:

```text
Enjoy your comfortable and well-paced adventure in Sabah!
(Plan quality: 96%)

We selected the Comfort Upgrade based on overall best fit.

Other options:
- Budget Saver (~90%, est. SGD 1079)
- Balanced Pick (~90%, est. SGD 1160)
```

---

# 🛠️ Technical Stack

## Backend

* FastAPI
* Uvicorn
* Pydantic

## AI & Orchestration

* OpenAI API
* Deterministic orchestration engine

## Messaging

* python-telegram-bot

## Infrastructure

* Render deployment
* httpx async requests

## Language

* Python 3.11+

---

# 📁 Project Structure

```text
app
├── agents
│   ├── core
│   │   ├── constraint_agent.py
│   │   └── intent_agent.py
│   ├── executor.py
│   ├── planner.py
│   ├── ranking.py
│   ├── registry.py
│   ├── reviewer.py
│   ├── router.py
│   └── variant.py
├── common
│   ├── config.py
│   ├── destination_normalizer.py
│   ├── guardrails.py
│   ├── openai_client.py
│   └── request_parser.py
├── intelligence
│   ├── conversation_interpreter.py
│   ├── destination_mapper.py
│   ├── feedback_interpreter.py
│   ├── feedback_selector.py
│   ├── personalization.py
│   ├── place_resolver.py
│   ├── realism.py
│   └── session_memory.py
├── main.py
├── orchestrator
│   ├── api.py
│   ├── state.py
│   └── workflow.py
├── pricing
│   └── engine.py
├── security
│   ├── __init__.py
│   └── abuse_guard.py
├── telegram_bot.py
└── tools
    └── travel.py
```

---

# 🔗 API Endpoints

| Endpoint            | Method | Description          |
| ------------------- | ------ | -------------------- |
| `/`                 | GET    | Root endpoint        |
| `/health`           | GET    | Health check         |
| `/docs`             | GET    | Swagger UI           |
| `/plan`             | POST   | Generate travel plan |
| `/telegram/webhook` | POST   | Telegram webhook     |

---

# 📦 Example Request Contract

```json
{
  "origin": "Singapore",
  "destinations": ["Sabah"],
  "budget": 1500,
  "duration_days": 4,
  "travelers": 1,
  "preferences": ["diving"],
  "include_state": false
}
```

Optional:

```json
"include_state": true
```

Enables full orchestration trace visibility for debugging and explainability.

---

# 📤 Example Response Structure

```json
{
  "message": "...",
  "request": {...},
  "executor": {...},
  "reviewer": {...},
  "ranking": {...},
  "selected_variant": {...},
  "variants": [...],
  "feedback": {...},
  "continuity": {...},
  "session_memory": {...},
  "debug_trace": [...],
  "errors": [],
  "status": "ok"
}
```

---

# ✈️ Travel Output Features

Generated itineraries may include:

* day-by-day activities
* estimated flight pricing
* hotel recommendations
* transport suggestions
* restaurant suggestions
* attraction recommendations
* cost breakdowns
* realism pacing
* variant comparisons

---

# 🔒 Governance & Security

## Security Decisions Implemented

* schema validation
* parser hygiene filtering
* deterministic routing
* controlled memory injection
* structured fallback orchestration
* debug-state gating

---

## Intentionally Avoided

The system currently does NOT support:

* payment execution
* credential persistence
* personal identity storage
* direct booking execution
* unsafe deep-link generation

---

# 🧪 Testing & Quality Assurance

## QA Coverage Includes

| Test Category          | Purpose                           |
| ---------------------- | --------------------------------- |
| Parsing Validation     | Detect malformed requests         |
| Ranking Consistency    | Ensure score alignment            |
| Variant Validation     | Verify deterministic outputs      |
| Telegram Formatting    | Prevent message corruption        |
| Realism Checks         | Avoid impossible itineraries      |
| Continuity Tests       | Validate follow-up coherence      |
| Debug Trace Validation | Confirm explainability visibility |

---

# 💬 Telegram Usage Guide

## Recommended Prompt Format

```text
[duration] [destination] budget [amount] [preferences]
```

Examples:

```text
4 days Sabah budget S$1500 diving
3 days Penang under SGD 1200 food and heritage
2 days Bangkok shopping
```

---

# 🔁 Follow-Up Interaction Examples

The bot supports conversational continuity.

| User Input             | Expected Behavior                |
| ---------------------- | -------------------------------- |
| "Cheaper option"       | Bias toward Budget Saver         |
| "More comfort please"  | Recompute toward Comfort Upgrade |
| "Less rushed"          | Reduce itinerary density         |
| "Same style as before" | Reuse prior preferences          |

---

# ⚠️ Current Limitations

## Known Constraints

* no real-time flight pricing
* no hotel APIs
* no persistent database
* no authentication layer
* no multi-city optimization
* regex-based NLP parsing
* no observability dashboard

---

# 🧭 Sprint Progression Summary

| Sprint      | Major Capability                               |
| ----------- | ---------------------------------------------- |
| Day 1 - 2   | FastAPI + Telegram + Planner/Executor/Reviewer |
| Sprint 3.4  | Deterministic ranking engine                   |
| Sprint 3.5  | Variant generation                             |
| Sprint 3.6  | Explainability layer                           |
| Sprint 3.7  | Adaptive feedback loop                         |
| Sprint 3.8  | Conversational continuity                      |
| Sprint 3.9  | Session memory                                 |
| Sprint 3.10 | Parser hygiene and leakage filtering           |
| Sprint 4.1  | Demo-ready API structure                       |
| Sprint 4.2  | Schema validation and debug gating             |
| Sprint 4.3  | Submission-grade documentation                 |

---

# 🔮 Future Roadmap

## Sprint 6.x — Real API Integration

Planned additions:

* flight APIs
* hotel APIs
* normalized external outputs
* API fallback logic

---

## Sprint 7.x — Persistent Personalization Memory

Planned capabilities:

* long-term preference memory
* adaptive scoring weights
* cross-session continuity

---

## Sprint 8.x — Booking Readiness

Planned enhancements:

* prefilled booking flows
* affiliate integration readiness
* deep-link booking support

---

## Sprint 9.x — Multi-Destination Intelligence

Future intelligence goals:

* route optimization
* sequencing logic
* travel-time realism

---

## Sprint 10.x — Agent Scaling

Target:

```text
8–15 specialized orchestration agents
```

Potential future agents:

* weather agent
* safety advisor
* visa intelligence
* budget optimizer
* recommendation explainer

---

# 🎨 Optional UX Improvements

## Softer Realism Messaging

Current:

```text
"The itinerary appears light for the trip duration and may underuse travel time."
```

Possible refinement:

```text
"The itinerary is paced more comfortably with additional flexibility."
```

---

## Enhanced Reviewer Tone

Current:

```text
"Your trip to Sabah looks exciting!"
```

Possible refinement:

```text
"Your Sabah itinerary balances diving, relaxation, and local exploration within your requested budget."
```

---

## Telegram Compact Rendering

Potential future upgrades:

* compact itinerary mode
* expandable sections
* multi-message rendering

---

# 📈 Engineering Principles

The platform prioritizes:

* explainability-first architecture
* deterministic reasoning
* modular orchestration
* lightweight infrastructure
* defensive fallbacks
* incremental extensibility

---

# 🧠 What This Project Demonstrates

This project demonstrates practical implementation of:

* multi-agent AI systems
* orchestration architecture
* explainable AI workflows
* API engineering
* structured output validation
* deterministic ranking systems
* Telegram bot integration
* cloud deployment
* conversational continuity
* adaptive personalization

---

# ⚠️ Disclaimer

This system provides estimated pricing and search-based recommendations only.

The platform:

* does not process payments
* does not guarantee live pricing
* does not provide official visa or safety advice
* should not be treated as a booking engine

Users should independently verify travel requirements and pricing before making decisions.

---

# 👤 Author - Sofian Bin Sidik (S7525372/I)

Developed as part of an AI Engineering and Data Science portfolio initiative focused on explainable multi-agent orchestration systems.