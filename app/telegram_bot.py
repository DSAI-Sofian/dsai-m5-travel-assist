import os
import asyncio
import httpx
from fastapi import FastAPI, Request, Response
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from app.common.request_parser import parse_trip_request

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("TELEGRAM_WEBHOOK_URL")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")

app = FastAPI(title="SEA Travel Planner Bot")
ptb = None
processed_update_ids = set()


async def send_telegram_message(chat_id: int, text: str):
    async with httpx.AsyncClient(timeout=30) as client:
        await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "disable_web_page_preview": True,
            },
        )


async def progress_updater(chat_id: int, message_id: int):
    try:
        await asyncio.sleep(60)
        await ptb.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="Almost ready...",
        )

        await asyncio.sleep(60)
        await ptb.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="Anytime now...",
        )
    except asyncio.CancelledError:
        pass
    except Exception:
        pass


async def start(update, context):
    if not update.message:
        return

    msg = (
        "Welcome to Travel Assist.\n\n"
        "To start building your itinerary, just say something like:\n"
        "4 days Kuala Lumpur $1500\n\n"
        "Optional add-ons:\n"
        "- food\n"
        "- shopping\n"
        "- culture\n"
        "- adventure\n\n"
        "Example:\n"
        "3 days KL food and shopping $800\n\n"
        "All itinerary prices are shown in SGD."
    )

    await update.message.reply_text(msg)


async def format_and_send(update: Update):
    global ptb

    text = update.message.text if update.message else ""
    chat_id = update.effective_chat.id

    payload = parse_trip_request(text)

    await ptb.bot.send_chat_action(chat_id=chat_id, action="typing")

    status_message = await ptb.bot.send_message(
        chat_id=chat_id,
        text="We are building your itinerary now...",
    )

    progress_task = asyncio.create_task(
        progress_updater(chat_id, status_message.message_id)
    )

    try:
        async with httpx.AsyncClient(timeout=180) as client:
            backend_base = BACKEND_URL.rstrip("/")
            r = await client.post(f"{backend_base}/plan", json=payload)
            r.raise_for_status()
            result = r.json()
    except Exception as e:
        progress_task.cancel()

        try:
            await ptb.bot.delete_message(
                chat_id=chat_id,
                message_id=status_message.message_id,
            )
        except Exception:
            pass

        await send_telegram_message(
            chat_id,
            f"Failed to generate trip.\nError: {str(e)}",
        )
        return

    progress_task.cancel()

    try:
        await ptb.bot.delete_message(
            chat_id=chat_id,
            message_id=status_message.message_id,
        )
    except Exception:
        pass

    executor = result.get("executor", {})
    reviewer = result.get("reviewer", {})
    cost_breakdown = executor.get("cost_breakdown", {})
    travel = executor.get("travel_details", {})
    nearby_attractions = executor.get("nearby_attractions", [])
    restaurants = executor.get("restaurants", [])
    daily_itinerary = executor.get("daily_itinerary", [])
    top = reviewer.get("top_3_options", [])

    realism = executor.get("realism", {})
    personalization = executor.get("personalization", {})

    pace = str(realism.get("pace", "unknown")).capitalize()
    style = str(personalization.get("travel_style", "general")).capitalize()

    within_budget = reviewer.get("within_budget")
    if within_budget is None:
        budget_fit_text = "Not assessed"
    else:
        budget_fit_text = "Yes" if within_budget else "No"

    request_data = result.get("request", payload)

    dest_text = (
        ", ".join(request_data.get("display_destinations", []))
        if request_data.get("display_destinations")
        else ", ".join(request_data.get("destinations", []))
        if request_data.get("destinations")
        else "Not detected"
)

    estimated_total = reviewer.get("estimated_total")
    estimated_total_text = (
        f"SGD {estimated_total:.0f}"
        if isinstance(estimated_total, (int, float))
        else f"SGD {estimated_total}"
    )

    msg = [
        "Trip plan ready",
        "",
        f"📍 Destination: {dest_text}",
        f"🗓 Duration: {request_data.get('duration_days')} days",
        f"💰 Budget fit: {budget_fit_text}",
        f"💵 Estimated cost: {estimated_total_text}",
        "",
        "🧭 Trip Overview",
        f"Trip pacing: {pace}",
        f"Style: {style}",
    ]

    summary = reviewer.get("user_message")
    if summary:
        msg.append("")
        msg.append(summary)

    msg.append("")
    msg.append("💰 Cost Breakdown")
    msg.append(f"- Flight: {cost_breakdown.get('flight', 'SGD 0')}")
    msg.append(f"- Hotel: {cost_breakdown.get('hotel', 'SGD 0')}")
    msg.append(f"- Activities: {cost_breakdown.get('activities', 'SGD 0')}")
    msg.append(f"- Transport: {cost_breakdown.get('local_transport', 'SGD 0')}")
    msg.append(f"- Food: {cost_breakdown.get('food', 'SGD 0')}")
    msg.append(f"- Total: {cost_breakdown.get('total', 'SGD 0')}")

    msg.append("")
    msg.append("✈️ Travel Details")

    flight = travel.get("flight", {})
    msg.append(f"- Flight: {flight.get('suggestion', '-')}")
    msg.append(f"  Price: {flight.get('estimated_price', '-')}")
    if flight.get("search_link"):
        msg.append(f"  Search: {flight.get('search_link')}")

    hotel = travel.get("hotel", {})
    msg.append("")
    msg.append(f"- Hotel: {hotel.get('name', '-')}")
    msg.append(f"  Price: {hotel.get('estimated_price', '-')}")
    msg.append(f"  Location: {hotel.get('location_note', '-')}")
    if hotel.get("booking_link"):
        msg.append(f"  Booking search: {hotel.get('booking_link')}")

    transport = travel.get("transport", {})
    msg.append("")
    msg.append(f"- Local transport: {transport.get('mode', '-')}")
    msg.append(f"  Cost: {transport.get('estimated_cost', '-')}")
    msg.append(f"  Notes: {transport.get('notes', '-')}")

    if nearby_attractions:
        msg.append("")
        msg.append("📍 Nearby Attractions")
        for item in nearby_attractions[:3]:
            if isinstance(item, dict):
                msg.append(
                    f"- {item.get('name', 'Attraction')} "
                    f"({item.get('distance_note', 'Not provided')})"
                )
                if item.get("search_link"):
                    msg.append(f"  Search: {item.get('search_link')}")
            else:
                msg.append(f"- {str(item)}")

    if restaurants:
        msg.append("")
        msg.append("🍜 Food & Restaurants")
        for item in restaurants[:3]:
            if isinstance(item, dict):
                msg.append(
                    f"- {item.get('name', 'Restaurant')} "
                    f"({item.get('distance_note', 'Not provided')})"
                )
                if item.get("search_link"):
                    msg.append(f"  Search: {item.get('search_link')}")
            else:
                msg.append(f"- {str(item)}")

    if daily_itinerary:
        msg.append("")
        msg.append("🗓 Day-by-day Itinerary")
        for item in daily_itinerary[:5]:
            if isinstance(item, dict):
                msg.append(f"Day {item.get('day', '-')}: {item.get('title', '')}")
                if item.get("details"):
                    msg.append(item.get("details"))
            else:
                msg.append(f"- {str(item)}")

    if top:
        msg.append("")
        msg.append("⭐ Top Options")
        for i, o in enumerate(top, 1):
            if isinstance(o, dict):
                msg.append(f"{i}. {o.get('name', '')}")
                if o.get("fit"):
                    msg.append(o.get("fit"))
            else:
                msg.append(f"{i}. {str(o)}")

    final_message = "\n".join(msg)
    print("FINAL MESSAGE:\n", final_message)

    try:
        await send_telegram_message(chat_id, final_message)
    except Exception as e:
        await send_telegram_message(chat_id, f"Send error: {str(e)}")


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
    ptb.add_handler(CommandHandler("start", start))
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
    global ptb, processed_update_ids

    data = await request.json()
    update = Update.de_json(data, ptb.bot)

    update_id = getattr(update, "update_id", None)
    if update_id in processed_update_ids:
        return Response(status_code=200)

    if update_id is not None:
        processed_update_ids.add(update_id)

    asyncio.create_task(ptb.process_update(update))

    return Response(status_code=200)