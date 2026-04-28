# 🌏 SEA Travel Planner — Multi-Agent AI Travel Assistant

> Project documentation and architecture evolution.

---

# 📌 Overview

SEA Travel Planner is a multi-agent AI-powered travel assistant designed to generate practical, budget-aware travel itineraries for Southeast Asia.

Unlike conventional chatbot-style travel assistants that provide generic recommendations, this system focuses on:

* structured outputs for single destinations
* deterministic scoring for multiple activities within single location
* explainable orchestration
* realism-aware planning
* budget validation
* conversational continuity

The platform evolved from a simple 3-agent architecture into a modular orchestration framework capable of adaptive travel planning, lightweight memory, and explainable decision-making.

The current implementation is optimized for Southeast Asia travel planning. 
The system may accept destinations outside Southeast Asia through fallback handling, but destination intelligence, cost assumptions, and itinerary quality are strongest for supported Southeast Asian destinations.

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

No secrets, user logs, admin chat IDs, or production credentials are stored in the repository. Runtime values are configured through environment variables in Render.

---

## 🤖 Link to SEA Travel Planner Bot

[Open SEA Travel Planner Bot](https://t.me/sofian_travelplanner_bot)

Destinations list used are based on common known destinations only. Reach out to me if there are any destinations that were not included and I will add them in manually.

Destination Intelligence is only scheduled to be implemented and deployed in Sprint 8.x.

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
* Multi-city itinerary orchestration
* Geographic destination routing
* Activity metadata intelligence
* Structured itinerary chunking
* Activity diversity engine
* Self-correcting itinerary validation
* Automatic itinerary repair and revalidation
* Travel transition awareness
* Long-duration itinerary support
* Structured pacing logic
* Meal-aware activity timing

## 🏙️ Multi-City Planning Status

The current implementation now supports structured multi-city itinerary orchestration for supported Southeast Asian destinations.

Sprint 6.x introduced deterministic geographic routing and destination-scoped activity planning, allowing the planner to generate more realistic multi-city travel flows.

Current capabilities include:

- destination-scoped itinerary generation
- city-aware activity routing
- transition-day handling
- pacing-aware scheduling
- route sequencing using deterministic progression
- structured long-duration itinerary support
- travel transition notes
- itinerary density balancing
- activity diversity controls
- self-correcting itinerary validation

Example supported progression:

```text
Ho Chi Minh City
→ Da Nang
→ Hoi An
→ Hanoi
```

---

# 🧠 Architecture Overview

## Sprint 6.x Intelligence Evolution

Sprint 6.x introduced a major transition from simple itinerary generation into deterministic realism-aware orchestration.

Key improvements introduced during Sprint 6.x include:

- structured itinerary chunking
- destination-scoped activity routing
- geographic isolation logic
- transition-day orchestration
- narrative enrichment
- activity metadata intelligence
- meal-aware activity timing
- diversity-aware itinerary generation
- self-correcting itinerary validation
- automatic itinerary repair and revalidation

The system now performs layered itinerary processing:

```text
Generate
→ Enrich
→ Validate
→ Repair
→ Revalidate
```

## Current Orchestration Pipeline

```text
User Request
→ abuse_guard
→ request_parser
→ routing
→ place_resolver
→ personalization
→ planner
→ executor
→ itinerary_chunker
→ activity_metadata
→ narrative_enricher
→ realism
→ variant
→ ranking
→ feedback
→ continuity
→ session_memory
→ reviewer
→ itinerary_validator
→ auto_repair
→ revalidation
```

---

# ⚙️ Multi-Agent Responsibilities

| Agent / Layer        | Responsibility                                                     | Guardrails / Controls           |
| -------------------- | ------------------------------------------------------------------ | ------------------------------- |
| Abuse Guard          | Pre-orchestration defensive gateway                                | Context filtering               |
| Request Parser       | Extracts destination, duration, budget, preferences                | Parser hygiene filtering        |
| Routing Agent        | Determines active orchestration path                               | Conditional execution           |
| Place Resolver       | Maps destinations and regional routing                             | Prevents destination drift      |
| Personalization      | Infers travel style and preferences                                | Controlled preference injection |
| Planner              | Generates structured planning assumptions                          | Scope control                   |
| Executor             | Produces itinerary and travel details                              | Structured JSON outputs         |
| Itinerary Chunker    | Builds structured multi-day itinerary blocks                       | Duration-aware pacing           |
| Activity Metadata    | Applies meal-aware and activity-aware semantic rules               | Timing validation               |
| Narrative Enricher   | Improves itinerary readability and sentence flow                   | Controlled semantic cleanup     |
| Realism Layer        | Evaluates pacing and feasibility                                   | Avoids unrealistic itineraries  |
| Variant Engine       | Creates multiple plan variants                                     | Deterministic transformations   |
| Ranking Engine       | Scores and selects best variant                                    | Weighted explainable scoring    |
| Feedback Interpreter | Applies user follow-up intent                                      | Controlled mutation             |
| Continuity Layer     | Maintains conversational coherence                                 | Context isolation               |
| Session Memory       | Reuses lightweight preferences                                     | Memory leakage filtering        |
| Reviewer             | Final validation and itinerary assessment                          | Quality and realism checks      |
| Itinerary Validator  | Detects repetition, timing conflicts, and weak itinerary structure | Validation scoring              |
| Auto-Repair Layer    | Repairs repeated or weak itinerary sections before final output    | Controlled deterministic repair |
| Revalidation Layer   | Confirms repaired itinerary quality                                | Final consistency enforcement   |

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
│   ├── activity_metadata.py
│   ├── conversation_interpreter.py
│   ├── destination_mapper.py
│   ├── destination_registry.py
│   ├── feedback_interpreter.py
│   ├── feedback_selector.py
│   ├── itinerary_chunker.py
│   ├── itinerary_validator.py
│   ├── narrative_enricher.py
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

* structured day-by-day itineraries
* morning / lunch / afternoon / evening activity planning
* multi-city route sequencing
* transition-day handling
* optional itinerary add-ons
* travel pacing notes
* meal-aware activity timing
* estimated flight pricing
* hotel recommendations
* transport suggestions
* restaurant suggestions
* attraction recommendations
* cost breakdowns
* realism pacing
* variant comparisons
* validation-aware itinerary repair
* automatic repetition reduction

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

| Test Category             | Purpose                                   |
| ------------------------- | ----------------------------------------- |
| Parsing Validation        | Detect malformed requests                 |
| Ranking Consistency       | Ensure score alignment                    |
| Variant Validation        | Verify deterministic outputs              |
| Telegram Formatting       | Prevent message corruption                |
| Realism Checks            | Avoid impossible itineraries              |
| Geographic Routing Checks | Prevent cross-city activity leakage       |
| Meal Timing Validation    | Prevent breakfast/dinner timing conflicts |
| Diversity Validation      | Reduce repeated itinerary activities      |
| Auto-Repair Validation    | Confirm itinerary correction behavior     |
| Revalidation Checks       | Verify repaired itinerary quality         |
| Continuity Tests          | Validate follow-up coherence              |
| Debug Trace Validation    | Confirm explainability visibility         |

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

To be addressed in future sprints...

## Known Constraints

* no land transportation option for ultra-low budget travel planning
* no real-time flight pricing
* no hotel APIs
* no persistent database
* no authentication layer
* deterministic destination intelligence is manually curated
* regex-assisted NLP parsing still used in some routing paths
* no observability dashboard
* no live transit-time estimation
* no external weather integration
* semantic phrasing still partially rule-based
* itinerary realism strongest for supported Southeast Asian destinations

---

# 🧭 Sprint Progression Summary

| Sprint      | Major Capability                            |
| ----------- | ------------------------------------------- |
| Sprint 1.1  | Orchestrator Refactor                       |
| Sprint 1.2  | Agent Registry                              |
| Sprint 1.3  | Agent Decomposition                         |
| Sprint 1.4  | Guardrails                                  |
| Sprint 2.1  | Destination Intelligence                    |
| Sprint 2.2  | Pricing Engine                              |
| Sprint 2.3  | Realism Layer                               |
| Sprint 2.4  | Personalization                             |
| Sprint 3.1  | Agent Expansion                             |
| Sprint 3.2  | Memory Layer                                |
| Sprint 3.3  | Machine Learning Component                  |
| Sprint 3.4  | Telegram Output Formatting                  |
| Sprint 3.5  | Deterministic Ranking Engine                |
| Sprint 3.6  | Variant Generation                          |
| Sprint 3.7  | Explainability Layer                        |
| Sprint 3.8  | Adaptive Feedback Loop                      |
| Sprint 3.9  | Conversational Continuity                   |
| Sprint 3.10 | Session Memory                              |
| Sprint 3.11 | Parser Hygiene and Leakage Filtering        |
| Sprint 4.1  | Demo-Ready API Structure                    |
| Sprint 4.2  | Schema Validation and Debug Gating          |
| Sprint 4.3  | Submission-Grade Documentation              |
| Sprint 5.1  | Lightweight Abuse Protection                |
| Sprint 5.2  | Deterministic Destination Routing           |
| Sprint 5.3  | Realism-Aware Variant Improvements          |
| Sprint 6.1  | Structured Itinerary Chunking               |
| Sprint 6.2  | Geographic Activity Isolation               |
| Sprint 6.3  | Multi-City Routing and Transition Logic     |
| Sprint 6.4  | Narrative Enrichment and Realism Refinement |
| Sprint 6.5  | Activity Metadata and Timing Validation     |
| Sprint 6.6  | Itinerary Validation and Self-Correction    |
| Sprint 6.7  | Activity Diversity and Density Engine       |
| Sprint 6.8  | Structured Meal Metadata Engine             |
| Sprint 6.9  | Automatic Itinerary Repair and Revalidation |

---

# 🔮 Future Roadmap

## Sprint 7.x — Budget Feasibility & Semantic Intelligence

Planned enhancements:

* budget feasibility engine
* transport-mode intelligence
* accommodation-tier enforcement
* hard budget validation
* route affordability scoring
* controlled semantic itinerary polishing
* reviewer-assisted narrative refinement

This phase improves both:
- affordability realism
- itinerary language quality

---

## Sprint 8.x — Advanced Destination Intelligence

Future intelligence goals:

* route optimization
* sequencing logic
* travel-time realism
* regional gateway logic
* live transit integration
* destination knowledge scaling

---

## Sprint 9.x — Real API Integration

Planned additions:

* flight APIs
* hotel APIs
* normalized external outputs
* API fallback logic
* live availability awareness

---

## Sprint 10.x — Persistent Personalization Memory

Planned capabilities:

* long-term preference memory
* adaptive scoring weights
* cross-session continuity
* preference evolution tracking

---

## Sprint 11.x — Booking Readiness

Planned enhancements:

* prefilled booking flows
* affiliate integration readiness
* deep-link booking support
* travel checkout preparation

---

## Sprint 12.x — Agent Scaling

Target:

```text
8–15 specialized orchestration agents
```

---

## Sprint 13.x — Conversational Expansion

Target:

```text
create more natural user interaction
```

Potential interactivity:

* Telegram voice support
* richer conversational follow-ups
* compact itinerary rendering
* adaptive interaction styles
* itinerary negotiation flows
* interactive refinement sessions

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

# 🏗️ Current Architecture Maturity

The current platform has evolved beyond a simple chatbot-style itinerary generator.

The system now includes:

- deterministic orchestration pipelines
- validation-aware itinerary generation
- automatic repair and revalidation loops
- explainability-first ranking systems
- structured pacing and realism scoring
- lightweight conversational continuity
- destination-scoped activity intelligence
- modular orchestration extensibility

The architecture now behaves closer to a lightweight orchestration platform than a traditional single-pass LLM chatbot.

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
* lightweight abuse guard

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

## 💬 Feedback & Suggested Improvements

Reviewers may suggest improvements by opening a GitHub Issue in this repository.

Please use Issues for:

- bug reports
- documentation suggestions
- feature ideas
- improvement recommendations

Pull Requests may be reviewed, but this repository is primarily maintained as a portfolio and educational review project.
