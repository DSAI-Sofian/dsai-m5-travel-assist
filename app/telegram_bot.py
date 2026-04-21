import os
import httpx
from fastapi import FastAPI, Request, Response
from telegram import Update
from telegram.ext import Application, MessageHandler, filters

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("TELEGRAM_WEBHOOK_URL")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")

app = FastAPI(title="SEA Travel Planner Bot")
ptb = None


async def send_telegram_message(chat_id: int, text: str):
    async with httpx.AsyncClient(timeout=30) as client:
        await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            },
        )


async def format_and_send(update: Update):
    global ptb

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

    await ptb.bot.send_chat_action(chat_id=chat_id, action="typing")

    status_message = await ptb.bot.send_message(
        chat_id=chat_id,
        text="_Agents are working on your request..._",
        parse_mode="Markdown",
    )

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            backend_base = BACKEND_URL.rstrip("/")
            r = await client.post(f"{backend_base}/plan", json=payload)
            r.raise_for_status()
            result = r.json()
    except Exception as e:
        try:
            await ptb.bot.delete_message(
                chat_id=chat_id,
                message_id=status_message.message_id,
            )
        except Exception:
            pass

        await send_telegram_message(
            chat_id,
            f"❌ Failed to generate trip.\nError: {str(e)}",
        )
        return

    try:
        await ptb.bot.delete_message(
            chat_id=chat_id,
            message_id=status_message.message_id,
        )
    except Exception:
        pass

    executor = result.get("executor", {})
    reviewer = result.get("reviewer", {})
    top = reviewer.get("top_3_options", [])
    cost_breakdown = executor.get("cost_breakdown", {})
    travel = executor.get("travel_details", {})
    places = executor.get("places", [])
    daily_itinerary = executor.get("daily_itinerary", [])

    msg = [
        "✈️ *Trip Plan Ready*",
        "",
        f"💰 Budget Fit: {'Yes' if reviewer.get('within_budget') else 'No'}",
        f"💵 Estimated Cost: SGD ${reviewer.get('estimated_total')}",
    ]

    summary = reviewer.get("user_message")
    if summary:
        msg.append("")
        msg.append(f"📝 {summary}")

    msg.append("")
    msg.append("📊 *Cost Breakdown:*")
    msg.append(f"- Flight: {cost_breakdown.get('flight', 'SGD 0')}")
    msg.append(f"- Hotel: {cost_breakdown.get('hotel', 'SGD 0')}")
    msg.append(f"- Activities: {cost_breakdown.get('activities', 'SGD 0')}")
    msg.append(f"- Local Transport: {cost_breakdown.get('local_transport', 'SGD 0')}")
    msg.append(f"- Food: {cost_breakdown.get('food', 'SGD 0')}")
    msg.append(f"- Total: {cost_breakdown.get('total', 'SGD 0')}")

    msg.append("")
    msg.append("🧭 *Travel Details:*")

    flight = travel.get("flight", {})
    msg.append(f"✈️ Flight: {flight.get('suggestion', '-')}")
    msg.append(f"   💰 {flight.get('estimated_price', '-')}")
    if flight.get("search_link"):
        msg.append(f"   🔗 {flight.get('search_link')}")

    hotel = travel.get("hotel", {})
    msg.append("")
    msg.append(f"🏨 Hotel: {hotel.get('name', '-')}")
    msg.append(f"   💰 {hotel.get('estimated_price', '-')}")
    msg.append(f"   📍 {hotel.get('location_note', '-')}")
    if hotel.get("booking_link"):
        msg.append(f"   🔗 {hotel.get('booking_link')}")

    transport = travel.get("transport", {})
    msg.append("")
    msg.append(f"🚗 Transport: {transport.get('mode', '-')}")
    msg.append(f"   💰 {transport.get('estimated_cost', '-')}")
    msg.append(f"   ⏱️ {transport.get('notes', '-')}")

    if places:
        msg.append("")
        msg.append("📍 *Key Places:*")
        for p in places[:3]:
            if isinstance(p, dict):
                msg.append(f"- {p.get('name', 'Place')}")
                if p.get("google_maps_link"):
                    msg.append(f"  🔗 {p.get('google_maps_link')}")
                msg.append(f"  🚶 {p.get('distance_note', 'Distance not provided')}")
            else:
                msg.append(f"- {str(p)}")

    if daily_itinerary:
        msg.append("")
        msg.append("🗓️ *Day-by-Day Itinerary:*")
        for item in daily_itinerary[:5]:
            if isinstance(item, dict):
                day = item.get("day", "-")
                title = item.get("title", "Plan")
                details = item.get("details", "")
                msg.append(f"*Day {day}: {title}*")
                if details:
                    msg.append(details)
            else:
                msg.append(f"- {str(item)}")

    msg.append("")
    msg.append("🌍 *Top Options:*")

    if not top:
        msg.append("- No options returned")
    else:
        for i, o in enumerate(top, 1):
            if isinstance(o, dict):
                name = o.get("name", f"Option {i}")
                fit = o.get("fit", "")
                msg.append(f"{i}. *{name}*")
                if fit:
                    msg.append(f"   {fit}")
            else:
                msg.append(f"{i}. {str(o)}")

    await send_telegram_message(chat_id, "\n".join(msg))


async def on_text(update, context):
    await format_and_send(update)


@app.on_event("startup")
async def startup():
    global ptb

    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    if not WEBHOOK_URL:
        raise RuntimeError("TELEGRAM_WEBHOOK_URL is not set")

    ptb = Application.builder().token(BOT_TOKEN).updater(None).build()
    ptb.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    await ptb.initialize()
    await ptb.start()
    await ptb.bot.set_webhook(url=WEBHOOK_URL)


@app.on_event("shutdown")
async def shutdown():
    global ptb

    if ptb is not None:
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
    global ptb

    data = await request.json()
    update = Update.de_json(data, ptb.bot)
    await ptb.process_update(update)
    return Response(status_code=200)