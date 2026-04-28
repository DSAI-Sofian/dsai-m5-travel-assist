# 🚀 Travel Assist Bot — Deployment User Guide

## 1. Purpose

This guide explains how to deploy and test the **Travel Assist Bot** in three environments:

1. **Localhost testing**
2. **Render cloud deployment**
3. **Telegram Bot setup using BotFather**

The project contains two FastAPI services:

| Service              | File                      | Purpose                                                              |
| -------------------- | ------------------------- | -------------------------------------------------------------------- |
| Backend API          | `app/orchestrator/api.py` | Handles `/plan`, `/health`, `/docs`, multi-agent workflow            |
| Telegram Bot Service | `app/telegram_bot.py`     | Receives Telegram webhook messages and sends requests to backend API |

Render supports deploying FastAPI as a Web Service, with build/start commands configured during service creation.

Telegram bots are created and configured through BotFather using commands such as `/newbot`, `/setdescription`, and `/setabouttext`.

---

# 🧪 Part 1 — Localhost Deployment for Testing

## 1.1 Open VS Code Terminal

From VS Code:

```bash
cd ~root/module_05/dsai-ft2-capstone-travel-assist
```

Adjust the path if your project folder is different.

---

## 1.2 Activate Virtual Environment

```bash
source .venv/bin/activate
```

Expected result:

```bash
(.venv) user@machine:~root/module_05/dsai-ft2-capstone-travel-assist$
```

---

## 1.3 Install Dependencies

Run:

```bash
pip install -r requirements.txt
```

---

## 1.4 Create `.env` File

Create a local `.env` file in the project root:

```bash
touch .env
```

Example `.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_WEBHOOK_URL=https://your-render-telegram-service.onrender.com/telegram/webhook
BACKEND_URL=http://127.0.0.1:8000
ADMIN_TELEGRAM_CHAT_ID=your_optional_telegram_chat_id
```

For local backend-only testing, the most important value is:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

---

# 🧠 1.5 Launch Backend API Locally

Run this command:

```bash
uvicorn app.orchestrator.api:app --reload --host 127.0.0.1 --port 8000
```

Expected terminal output should include something similar to:

```bash
Uvicorn running on http://127.0.0.1:8000
```

---

## 1.6 Local Backend URLs

| Purpose              | URL                                  |
| -------------------- | ------------------------------------ |
| Root endpoint        | `http://127.0.0.1:8000/`             |
| Health check         | `http://127.0.0.1:8000/health`       |
| Swagger docs         | `http://127.0.0.1:8000/docs`         |
| OpenAPI JSON         | `http://127.0.0.1:8000/openapi.json` |
| Travel plan endpoint | `http://127.0.0.1:8000/plan`         |

---

# ✅ 1.7 Test Local Health Endpoint

Open a second terminal and run:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

---

# ✅ 1.8 Test Root Endpoint

```bash
curl http://127.0.0.1:8000/
```

Expected response should look similar to:

```json
{
  "message": "SEA Travel Planner API is running.",
  "docs_url": "/docs",
  "health_url": "/health"
}
```

---

# ✅ 1.9 Test `/plan` Endpoint

Use this `curl` command:

```bash
curl -X POST http://127.0.0.1:8000/plan \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Singapore",
    "destinations": ["Penang"],
    "budget": 1000,
    "duration_days": 4,
    "travelers": 1,
    "preferences": ["food"],
    "include_state": false
  }'
```

Expected result:

```json
{
  "message": "...",
  "request": {...},
  "executor": {...},
  "reviewer": {...},
  "ranking": {...},
  "status": "ok"
}
```

---

# ✅ 1.10 Test Follow-Up Request Locally

For the tests below, open a 2nd terminal window.
- 1st window for launching uvicorn
- 2nd window to input instructions below

Test 1: add more food places.

```bash
curl -X POST http://127.0.0.1:8000/plan \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Singapore",
    "destinations": ["Penang"],
    "budget": 1000,
    "duration_days": 4,
    "travelers": 1,
    "preferences": ["food"],
    "feedback": "add more food places",
    "include_state": false
  }'
```

Test 2: add more activities.

```bash
curl -X POST http://127.0.0.1:8000/plan \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Singapore",
    "destinations": ["Penang"],
    "budget": 1000,
    "duration_days": 4,
    "travelers": 1,
    "preferences": ["food"],
    "feedback": "add more activities",
    "include_state": false
  }'
```

---

# 🔍 1.11 Test with Debug State

Use `include_state: true` if you want to inspect agent traces and internal workflow state.

```bash
curl -X POST http://127.0.0.1:8000/plan \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Singapore",
    "destinations": ["Vietnam"],
    "budget": 2000,
    "duration_days": 10,
    "travelers": 1,
    "preferences": ["culture"],
    "include_state": true
  }'
```

Look for:

```json
"debug_trace": [...]
```

and:

```json
"errors": [...]
```

---

# 🛑 1.12 Stop Local Server

In the terminal running Uvicorn:

```bash
CTRL + C
```

Then deactivate virtual environment:

```bash
deactivate
```

---

# 🤖 1.13 Local Telegram Testing Note

The Telegram bot service requires a public HTTPS webhook URL.

Localhost alone is usually not enough because Telegram must reach your app over the public internet. Telegram supports webhook-based updates where Telegram sends HTTPS POST requests to your configured webhook URL. ([Telegram][1])

For local Telegram webhook testing, use either:

```text
ngrok
```

or deploy the Telegram service to Render.

Recommended for this project:

```text
Use localhost for backend API testing.
Use Render for Telegram bot testing.
```

---

# ☁️ Part 2 — Deploy Backend API on Render

## 2.1 Render Deployment Structure

Recommended Render setup:

| Render Service       | Source File               | Start Command                                                  |
| -------------------- | ------------------------- | -------------------------------------------------------------- |
| Backend API Service  | `app/orchestrator/api.py` | `uvicorn app.orchestrator.api:app --host 0.0.0.0 --port $PORT` |
| Telegram Bot Service | `app/telegram_bot.py`     | `uvicorn app.telegram_bot:app --host 0.0.0.0 --port $PORT`     |

Render Web Services host dynamic apps such as FastAPI and provide public URLs for deployed services. ([Render][2])

---

# 🖼️ 2.2 Suggested Screenshot Placeholders

Create this folder in your repo if you want to add images later:

```bash
mkdir -p docs/images
```

Recommended screenshots to capture manually from Render:

```markdown
![Render Dashboard](docs/images/render-dashboard.png)

![Render New Web Service](docs/images/render-new-web-service.png)

![Render Environment Variables](docs/images/render-env-vars.png)

![Render Deploy Logs](docs/images/render-deploy-logs.png)

![Render Service URL](docs/images/render-service-url.png)
```

---

# 🧱 2.3 Create Backend API Web Service

## Step 1 — Go to Render Dashboard

Open Render:

```text
https://dashboard.render.com
```

## Step 2 — Click “New”

Select:

```text
Web Service
```

## Step 3 — Connect GitHub Repository

Choose your GitHub repository containing the Travel Assist Bot code.

## Step 4 — Configure Backend API Service

Recommended settings:

| Setting       | Value                                                          |
| ------------- | -------------------------------------------------------------- |
| Name          | `travel-assist-api`                                            |
| Runtime       | `Python 3`                                                     |
| Branch        | `main`                                                         |
| Build Command | `pip install -r requirements.txt`                              |
| Start Command | `uvicorn app.orchestrator.api:app --host 0.0.0.0 --port $PORT` |
| Instance Type | Free / Starter depending on need                               |

Render’s FastAPI deployment guide uses Web Service setup with build/start commands for FastAPI apps. ([Render][3])

---

## 2.4 Backend API Environment Variables

In Render:

```text
Service → Environment → Add Environment Variable
```

Add:

| Key              | Value               |
| ---------------- | ------------------- |
| `OPENAI_API_KEY` | Your OpenAI API key |

Optional:

| Key                               | Value  |
| --------------------------------- | ------ |
| `ABUSE_WARNING_LIMIT_PER_MINUTE`  | `5`    |
| `ABUSE_BLOCK_LIMIT_PER_5_MINUTES` | `10`   |
| `ABUSE_BLOCK_SECONDS`             | `1800` |

---

## 2.5 Deploy Backend API

Click:

```text
Manual Deploy → Deploy latest commit
```

Wait for logs to show successful deployment.

---

## 2.6 Get Backend API URL

After deployment, Render provides a public service URL such as:

```text
https://travel-assist-api.onrender.com
```

Save this value.

This will become:

```env
BACKEND_URL=https://travel-assist-api.onrender.com
```

for the Telegram service.

---

## 2.7 Test Backend API on Render

Health check:

```bash
curl https://travel-assist-api.onrender.com/health
```

Expected:

```json
{"status":"ok"}
```

Root:

```bash
curl https://travel-assist-api.onrender.com/
```

Docs:

```text
https://travel-assist-api.onrender.com/docs
```

Test `/plan`:

```bash
curl -X POST https://travel-assist-api.onrender.com/plan \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Singapore",
    "destinations": ["Penang"],
    "budget": 1000,
    "duration_days": 4,
    "travelers": 1,
    "preferences": ["food"]
  }'
```

---

# 📲 Part 3 — Deploy Telegram Bot Service on Render

## 3.1 Create Second Web Service

In Render Dashboard:

```text
New → Web Service
```

Connect the same GitHub repository.

---

## 3.2 Configure Telegram Bot Service

| Setting       | Value                                                      |
| ------------- | ---------------------------------------------------------- |
| Name          | `travel-assist-telegram-bot`                               |
| Runtime       | `Python 3`                                                 |
| Branch        | `main`                                                     |
| Build Command | `pip install -r requirements.txt`                          |
| Start Command | `uvicorn app.telegram_bot:app --host 0.0.0.0 --port $PORT` |
| Instance Type | Free / Starter                                             |

---

## 3.3 Telegram Bot Environment Variables

Add these to the Telegram bot Render service:

| Key                      | Value                                                              |
| ------------------------ | ------------------------------------------------------------------ |
| `TELEGRAM_BOT_TOKEN`     | Bot token from BotFather                                           |
| `TELEGRAM_WEBHOOK_URL`   | `https://travel-assist-telegram-bot.onrender.com/telegram/webhook` |
| `BACKEND_URL`            | `https://travel-assist-api.onrender.com`                           |
| `ADMIN_TELEGRAM_CHAT_ID` | Optional admin chat ID                                             |

Optional abuse guard variables:

| Key                               | Value  |
| --------------------------------- | ------ |
| `ABUSE_WARNING_LIMIT_PER_MINUTE`  | `5`    |
| `ABUSE_BLOCK_LIMIT_PER_5_MINUTES` | `10`   |
| `ABUSE_BLOCK_SECONDS`             | `1800` |

---

## 3.4 How to Construct Telegram Webhook URL

If your Telegram bot service URL is:

```text
https://travel-assist-telegram-bot.onrender.com
```

then webhook URL should be:

```text
https://travel-assist-telegram-bot.onrender.com/telegram/webhook
```

Set this in Render as:

```env
TELEGRAM_WEBHOOK_URL=https://travel-assist-telegram-bot.onrender.com/telegram/webhook
```

The app automatically sets the Telegram webhook during startup using the configured webhook URL.

---

## 3.5 Deploy Telegram Service

Click:

```text
Manual Deploy → Deploy latest commit
```

Wait for the logs to show successful startup.

Expected behavior:

```text
Telegram bot service starts
Webhook is set automatically
Health endpoint is available
```

---

## 3.6 Test Telegram Service Health

```bash
curl https://travel-assist-telegram-bot.onrender.com/health
```

Expected:

```json
{"status":"ok"}
```

---

# 🤖 Part 4 — Create Telegram Bot with BotFather

Telegram bots are created through BotFather. The Telegram documentation states that `/newbot` is used to create a new bot, and BotFather provides the bot token after creation. ([Telegram][4])

---

## 4.1 Open BotFather

In Telegram, search for:

```text
@BotFather
```

Open the verified BotFather chat.

---

## 4.2 Create New Bot

Send:

```text
/newbot
```

BotFather will ask for:

```text
Bot name
```

Example:

```text
Travel Assist by Sofian
```

Then BotFather will ask for:

```text
Bot username
```

Example:

```text
travel_assist_sofian_bot
```

Telegram bot usernames usually need to end with:

```text
bot
```

or:

```text
_bot
```

---

## 4.3 Save Bot Token

BotFather will return a token similar to:

```text
1234567890:ABCDEF_your_token_here
```

Add this to Render:

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCDEF_your_token_here
```

Do not commit this token to GitHub.

---

# 📝 Part 5 — Configure Bot Profile

## 5.1 Set Bot Description

Send to BotFather:

```text
/setdescription
```

Choose your bot.

Suggested description:

```text
I am a multi-agent AI assistant that generates practical, budget-aware travel plans to South-East Asia.

I currently focus mainly on flight-based travel planning. Land transport such as buses and rail may be added in future versions.

Prices listed are indicative only and bookings/payments must be made directly with service providers.
```

BotFather supports setting a bot description through configuration commands. ([docs.radist.online][5])

---

## 5.2 Set About Text

Send:

```text
/setabouttext
```

Suggested about text:

```text
Multi-agent AI travel planner for South-East Asia.
```

The about text appears before the user starts the bot. Telegram documents `/setabouttext` as a BotFather configuration command. ([Telegram][4])

---

## 5.3 Set Bot Commands

Send:

```text
/setcommands
```

Suggested command list:

```text
start - Start Travel Assist
help - Show usage instructions
```

---

## 5.4 Set Bot Profile Photo

Send:

```text
/setuserpic
```

Then upload the bot profile image.

---

# ✏️ Part 6 — Edit Existing Telegram Bot

To edit an existing bot:

```text
/mybots
```

Then select your bot.

Common edit options:

| BotFather Command | Purpose                                 |
| ----------------- | --------------------------------------- |
| `/setname`        | Change bot display name                 |
| `/setdescription` | Change bot profile description          |
| `/setabouttext`   | Change short about text                 |
| `/setuserpic`     | Change profile picture                  |
| `/setcommands`    | Change available commands               |
| `/revoke`         | Revoke old token and generate new token |

---

# 🔎 Part 7 — Get Telegram Chat ID

## Option A — Use Telegram Bot API `getUpdates`

Before webhook is set, send a message to your bot manually, such as:

```text
hello
```

Then run:

```bash
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```

Look for:

```json
"chat": {
  "id": 123456789
}
```

Use that value as:

```env
ADMIN_TELEGRAM_CHAT_ID=123456789
```

Telegram documents `getUpdates` as one way to receive bot updates, while webhooks are the alternative method. ([Telegram][1])

---

## Option B — If Webhook Is Already Set

Telegram webhooks and `getUpdates` are mutually exclusive update methods. ([Telegram][1])

If webhook is already active, use:

```bash
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

To temporarily remove webhook:

```bash
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook
```

Then send a message to the bot and use:

```bash
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```

After retrieving chat ID, restart the Render Telegram service so the app sets the webhook again.

---

# 🔗 Part 8 — Verify Telegram Webhook

Run:

```bash
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

Expected result should include your Render webhook URL:

```json
{
  "ok": true,
  "result": {
    "url": "https://travel-assist-telegram-bot.onrender.com/telegram/webhook"
  }
}
```

Telegram’s `setWebhook` method is used to specify the HTTPS URL where Telegram sends bot updates. ([Telegram Bot PHP SDK][6])

---

# ▶️ Part 9 — Start Bot in Telegram

Open your bot in Telegram.

Click:

```text
Start
```

or send:

```text
/start
```

Expected response:

```text
Welcome to Travel Assist.

Hello! Tell me your expected:
[duration] [destination] budget [amount] [preferences]

Example:
4 days Sabah budget S$1500 diving
```

---

# 🧪 Part 10 — Telegram Test Queries

## Basic Query

```text
4D3N Penang 1000 food
```

Expected:

* destination detected as Penang
* duration detected as 4 days
* budget detected as SGD 1000
* food preference detected

---

## Culture Query

```text
4D3N Sarawak $1200 culture
```

Expected:

* destination detected as Sarawak
* primary city search may use Kuching
* budget detected as SGD 1200
* culture preference detected

---

## Long Trip Query

```text
10 days Vietnam $2000 culture
```

Expected:

* duration detected as 10 days
* itinerary displays multiple days
* budget detected as SGD 2000

---

## Follow-Up: Add Food

```text
add more food places
```

Expected:

* restaurants list expands
* food budget increases
* total budget increases

---

## Follow-Up: Add Activities

```text
add more activities
```

Expected:

* nearby attractions expand
* itinerary receives optional activity notes
* activities budget increases
* total budget increases

---

## Follow-Up: Relax Pace

```text
make it less rushed
```

Expected:

* pace becomes relaxed
* itinerary notes include buffer/rest time

---

# 🧯 Part 11 — Troubleshooting

## 11.1 `/health` Fails on Render

Check:

```text
Render → Service → Logs
```

Common causes:

* missing dependency
* wrong start command
* wrong module path
* app crash during startup

Correct backend start command:

```bash
uvicorn app.orchestrator.api:app --host 0.0.0.0 --port $PORT
```

Correct Telegram start command:

```bash
uvicorn app.telegram_bot:app --host 0.0.0.0 --port $PORT
```

---

## 11.2 Telegram Bot Does Not Respond

Check:

```bash
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

Confirm webhook URL is:

```text
https://your-telegram-service.onrender.com/telegram/webhook
```

Also check:

* `TELEGRAM_BOT_TOKEN`
* `TELEGRAM_WEBHOOK_URL`
* `BACKEND_URL`
* Render logs

---

## 11.3 Backend Works but Telegram Fails

Check Telegram service environment variable:

```env
BACKEND_URL=https://your-api-service.onrender.com
```

Then test manually:

```bash
curl https://your-api-service.onrender.com/health
```

---

## 11.4 `/plan` Returns Error

Check:

```env
OPENAI_API_KEY
```

Also test local `/plan` with:

```bash
curl -X POST https://your-api-service.onrender.com/plan \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Singapore",
    "destinations": ["Penang"],
    "budget": 1000,
    "duration_days": 4,
    "travelers": 1,
    "preferences": ["food"]
  }'
```

---

## 11.5 Telegram Shows Old Behavior After Code Change

Possible causes:

1. Render has not redeployed latest commit.
2. Wrong branch selected.
3. Build cache still using previous deployment.
4. You updated backend service but not Telegram service.
5. You updated Telegram service but not backend service.

Fix:

```text
Render → Manual Deploy → Deploy latest commit
```

Do this for both services if required.

---

# 🔐 Part 12 — Security Notes

Do not commit these values to GitHub:

```env
OPENAI_API_KEY
TELEGRAM_BOT_TOKEN
ADMIN_TELEGRAM_CHAT_ID
```

Use Render Environment Variables instead.

---

# ✅ Part 13 — Deployment Checklist

## Localhost

* [ ] Virtual environment activated
* [ ] Dependencies installed
* [ ] `.env` configured
* [ ] Backend starts with Uvicorn
* [ ] `/health` returns OK
* [ ] `/docs` loads
* [ ] `/plan` works with `curl`

## Render Backend API

* [ ] Web Service created
* [ ] Correct build command
* [ ] Correct start command
* [ ] `OPENAI_API_KEY` added
* [ ] `/health` works
* [ ] `/plan` works

## Render Telegram Service

* [ ] Second Web Service created
* [ ] Correct Telegram start command
* [ ] `TELEGRAM_BOT_TOKEN` added
* [ ] `TELEGRAM_WEBHOOK_URL` added
* [ ] `BACKEND_URL` added
* [ ] `/health` works
* [ ] Webhook verified

## Telegram Bot

* [ ] Bot created using BotFather
* [ ] Token saved securely
* [ ] Description added
* [ ] About text added
* [ ] Commands added
* [ ] `/start` works
* [ ] Test query works
* [ ] Follow-up query works

---

# 🧾 Appendix A — Key Commands

## Local Backend

```bash
uvicorn app.orchestrator.api:app --reload --host 127.0.0.1 --port 8000
```

## Render Backend Start Command

```bash
uvicorn app.orchestrator.api:app --host 0.0.0.0 --port $PORT
```

## Render Telegram Start Command

```bash
uvicorn app.telegram_bot:app --host 0.0.0.0 --port $PORT
```

## Health Check

```bash
curl http://127.0.0.1:8000/health
```

```bash
curl https://your-api-service.onrender.com/health
```

```bash
curl https://your-telegram-service.onrender.com/health
```

## Test `/plan`

```bash
curl -X POST http://127.0.0.1:8000/plan \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Singapore",
    "destinations": ["Penang"],
    "budget": 1000,
    "duration_days": 4,
    "travelers": 1,
    "preferences": ["food"]
  }'
```

## Telegram Webhook Info

```bash
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

## Telegram Updates

```bash
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```

## Delete Webhook

```bash
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook
```

---

# 🎯 Final Notes

For demonstration, the recommended flow is:

```text
1. Open Render backend /health
2. Open Render backend /docs
3. Send Telegram /start
4. Send: 4D3N Penang 1000 food
5. Send: add more food places
6. Send: add more activities
7. Explain multi-agent orchestration flow
```

This demonstrates:

* deployment success
* Telegram integration
* FastAPI backend
* multi-agent workflow
* follow-up continuity
* budget-aware updates
* adaptive itinerary refinement

---

[1]: https://core.telegram.org/bots/api?utm_source=chatgpt.com "Telegram Bot API"
[2]: https://render.com/docs/web-services?utm_source=chatgpt.com "Web Services"
[3]: https://render.com/docs/deploy-fastapi?utm_source=chatgpt.com "Deploy a FastAPI App"
[4]: https://core.telegram.org/bots/features?utm_source=chatgpt.com "Telegram Bot Features"
[5]: https://docs.radist.online/docs/our-products/radist-web/connections/telegram-bot/instructions-for-creating-and-configuring-a-bot-in-botfather?utm_source=chatgpt.com "Instructions for creating and configuring a bot in BotFather"
[6]: https://telegram-bot-sdk.readme.io/reference/setwebhook?utm_source=chatgpt.com "setWebhook"