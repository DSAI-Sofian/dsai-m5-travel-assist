import os
import httpx
from fastapi import FastAPI, Request, Response
from telegram import Update
from telegram.ext import Application, MessageHandler, filters

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
WEBHOOK_URL = os.environ["TELEGRAM_WEBHOOK_URL"]
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")

ptb = Application.builder().token(BOT_TOKEN).updater(None).build()
app = FastAPI(title="SEA Travel Planner Bot")


async def send_telegram_message(chat_id: int, text: str):
    async with httpx.AsyncClient(timeout=30) as client:
        await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text},
        )


async def format_and_send(update: Update):
    text = update.message.text if update.message else ""
    chat_id = update.effective_chat.id

    payload = {
        "origin": "Singapore",
        "destinations": ["Malaysia", "Indonesia"],
        "budget": 1200,
        "duration_days": 5,
        "travelers": 1,
        "preferences": [text],
    }

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            backend_base = BACKEND_URL.rstrip("/")
            r = await client.post(f"{backend_base}/plan", json=payload)
            r.raise_for_status()
            result = r.json()
    except Exception as e:
        await send_telegram_message(
            chat_id,
            f"Sorry, the trip planner is currently unavailable.\nError: {str(e)}"
        )
        return

    reviewer = result.get("reviewer", {})
    top = reviewer.get("top_3_options", [])

    msg = [
        "Trip plan ready.",
        f"Within budget: {reviewer.get('within_budget')}",
        f"Estimated total: {reviewer.get('estimated_total')}",
        "",
        "Top options:",
    ]

    if not top:
        msg.append("- No options returned")
    else:
        for o in top:
            if isinstance(o, dict):
                name = o.get("name", "Option")
                fit = o.get("fit", "")
                if fit:
                    msg.append(f"- {name}: {fit}")
                else:
                    msg.append(f"- {name}")
            else:
                msg.append(f"- {str(o)}")

    await send_telegram_message(chat_id, "\n".join(msg))


async def on_text(update, context):
    await format_and_send(update)


ptb.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))


@app.on_event("startup")
async def startup():
    await ptb.bot.set_webhook(url=WEBHOOK_URL)
    await ptb.initialize()
    await ptb.start()


@app.on_event("shutdown")
async def shutdown():
    await ptb.stop()
    await ptb.shutdown()


@app.get("/")
def root():
    return {
        "message": "SEA Travel Planner Telegram bot is running.",
        "health_url": "/health",
        "webhook_url": "/telegram/webhook",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, ptb.bot)
    await ptb.process_update(update)
    return Response(status_code=200)