# 🌏 SEA Travel Planner — Multi-Agent AI Travel Assistant

## 📌 Overview

SEA Travel Planner is a multi-agent AI-powered travel assistant designed to generate **practical, budget-aware travel plans** for Southeast Asia.

Unlike typical AI chatbots that provide high-level suggestions, this system delivers **actionable travel outputs**, including:

* 💰 Budget validation (SGD-based)
* ✈️ Flight suggestions with search links
* 🏨 Hotel recommendations with booking links
* 🚗 Local transport guidance
* 📍 Google Maps links for attractions
* 🗓️ Day-by-day itinerary
* 📊 Cost breakdown (flight, hotel, activities, etc.)

The system is deployed as a **Telegram bot + FastAPI backend**, making it accessible via chat.

---

## 🧠 Architecture

This project uses a **multi-agent design pattern**:

| Agent        | Role                                                   |
| ------------ | ------------------------------------------------------ |
| **Planner**  | Interprets user request and structures the travel plan |
| **Executor** | Generates itinerary, travel details, costs, and links  |
| **Reviewer** | Validates plan, checks budget, ranks top options       |

### Flow

User → Telegram Bot → FastAPI `/plan` → Planner → Executor → Reviewer → Telegram Response

---

## ⚙️ Tech Stack

* **Backend:** FastAPI
* **AI Engine:** OpenAI API
* **Bot Interface:** Telegram Bot API
* **Deployment:** Render
* **HTTP Client:** httpx
* **Language:** Python 3.11+

---

## 📁 Project Structure

```
app/
├── agents/
│   ├── planner.py
│   ├── executor.py
│   ├── reviewer.py
│
├── orchestrator/
│   ├── workflow.py
│   ├── api.py
│
├── common/
│   ├── openai_client.py
│
├── telegram_bot.py
├── main.py

requirements.txt
Dockerfile
```

---

## 🚀 Features

### ✅ Core Capabilities

* Natural language travel requests (via Telegram)
* Multi-agent reasoning pipeline
* SGD-based budgeting
* Structured JSON outputs
* Robust error handling

### ✨ Enhanced Outputs

* Flight suggestions (Google Flights links)
* Hotel recommendations (Booking.com links)
* Transport suggestions (Grab, taxi, etc.)
* Google Maps links for places
* Day-by-day itinerary
* Cost breakdown

---

## 🔧 Requirements

* Python **3.11+**
* Telegram Bot Token
* OpenAI API Key
* Render account (for deployment)

---

## 🔑 Environment Variables

Create a `.env` file or configure in Render:

```
OPENAI_API_KEY=your_openai_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_WEBHOOK_URL=https://your-bot-url.onrender.com/telegram/webhook
BACKEND_URL=https://your-backend-url.onrender.com
```

---

## 🧪 Running Locally (Simple)

### Step 1 — Setup environment

```bash
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
# OR
.venv\Scripts\activate      # Windows
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Start backend

```bash
uvicorn app.main:app --reload
```

### Step 4 — Start Telegram bot

```bash
uvicorn app.telegram_bot:app --reload --port 8001
```

---

## 🌐 Deployment (Render)

### Backend Service

* Build Command:

  ```
  pip install -r requirements.txt
  ```

* Start Command:

  ```
  uvicorn app.main:app --host 0.0.0.0 --port 10000
  ```

---

### Bot Service

* Start Command:

  ```
  uvicorn app.telegram_bot:app --host 0.0.0.0 --port 10000
  ```

---

## 🔗 Key Endpoints

| Endpoint            | Description          |
| ------------------- | -------------------- |
| `/`                 | Root check           |
| `/health`           | Health check         |
| `/docs`             | Swagger UI           |
| `/plan`             | Generate travel plan |
| `/telegram/webhook` | Telegram webhook     |

---

## 💬 Example Telegram Interaction

**User input:**

```
3-day shopping trip to Penang under SGD 1200
```

**Bot output includes:**

* Budget fit ✅
* Estimated total (SGD)
* Cost breakdown
* Flight + hotel suggestions
* Transport guidance
* Google Maps links
* Day-by-day itinerary
* Top 3 options

---

## ⚠️ Limitations

* Uses AI-generated estimates (not real-time pricing)
* No direct booking integration yet
* No persistent user memory
* Limited personalization across sessions

---

## 🔮 Future Enhancements

* Real-time flight & hotel APIs
* User preference memory
* Multi-turn conversation support
* Web UI dashboard
* Booking integration
* Location-aware optimization

---

## 🧩 Key Engineering Decisions

* **JSON-first design** for stable agent communication
* **Defensive parsing** to handle LLM variability
* **Multi-agent separation** for modular reasoning
* **SGD normalization** for localized UX
* **Webhook-based bot deployment** for scalability

---

## 📊 What This Project Demonstrates

* Multi-agent AI system design
* API orchestration (FastAPI)
* LLM prompt engineering
* Cloud deployment (Render)
* Telegram bot integration
* Structured output validation
* Product-oriented AI design

---

## 📄 License

MIT License

---

## 👤 Author

Developed as part of an AI Engineering / Data Science portfolio project.

---

## ⭐ Final Note

This project goes beyond a typical chatbot by combining:

* reasoning
* structured outputs
* real-world usability

It demonstrates how AI can be integrated into a **practical end-to-end system**, not just a prototype.