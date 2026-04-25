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


def _format_money(value) -> str:
    if value is None:
        return "Not available"

    text = str(value)

    if text.upper().startswith("SGD"):
        return text

    try:
        amount = float(text)
        if amount.is_integer():
            return f"SGD {int(amount)}"
        return f"SGD {amount:.2f}"
    except Exception:
        return text


def _safe_list(items, limit=3):
    if not isinstance(items, list):
        return []
    return items[:limit]


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
            text="Almost ready. Finalizing itinerary options...",
        )

        await asyncio.sleep(60)
        await ptb.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="Still working. Checking route, cost, and itinerary quality...",
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
        "Send a trip request like:\n"
        "4 days Sabah budget S$1500 diving\n\n"
        "You can also refine the plan after that:\n"
        "- cheaper option\n"
        "- more comfort please\n"
        "- add more food places\n"
        "- make it less rushed\n"
        "- add nature activities\n\n"
        "All itinerary prices are shown in SGD."
    )

    await update.message.reply_text(msg)


def build_telegram_summary(result: dict, fallback_payload: dict) -> str:
    request_data = result.get("request", fallback_payload) or {}
    executor = result.get("executor", {}) or {}
    reviewer = result.get("reviewer", {}) or {}
    ranking = result.get("ranking", {}) or {}
    selected_variant = result.get("selected_variant", {}) or {}
    feedback = result.get("feedback", {}) or {}
    continuity = result.get("continuity", {}) or {}

    cost_breakdown = executor.get("cost_breakdown", {}) or {}
    travel = executor.get("travel_details", {}) or {}
    realism = executor.get("realism", {}) or {}
    personalization = executor.get("personalization", {}) or {}

    daily_itinerary = executor.get("daily_itinerary", []) or []
    attractions = executor.get("nearby_attractions", []) or []
    restaurants = executor.get("restaurants", []) or []

    destinations = request_data.get("display_destinations") or request_data.get("destinations") or []
    dest_text = ", ".join(destinations) if destinations else "Not detected"

    duration = request_data.get("duration_days", "-")
    budget = request_data.get("budget")
    budget_text = _format_money(budget) if budget else "Not provided"

    selected_label = (
        selected_variant.get("variant_label")
        or executor.get("variant_label")
        or "Recommended Plan"
    )

    score_pct = ranking.get("score_pct")
    score_text = f"{float(score_pct):.0f}%" if isinstance(score_pct, (int, float)) else "Not scored"

    estimated_total = (
        ranking.get("estimated_total")
        or reviewer.get("estimated_total")
        or cost_breakdown.get("total")
    )

    msg = [
        "✅ Trip plan ready",
        "",
        f"📍 Destination: {dest_text}",
        f"🗓 Duration: {duration} days",
        f"💼 Selected plan: {selected_label}",
        f"⭐ Plan quality: {score_text}",
        f"💵 Estimated cost: {_format_money(estimated_total)}",
        f"🎯 Budget: {budget_text}",
        "",
        "🧭 Trip overview",
        f"- Pace: {str(realism.get('pace', 'balanced')).capitalize()}",
        f"- Style: {str(personalization.get('travel_style', 'general')).capitalize()}",
    ]

    if feedback.get("has_feedback"):
        msg.append(f"- Feedback applied: {feedback.get('reason', 'Yes')}")

    if continuity.get("has_followup"):
        adjustments = ", ".join(continuity.get("requested_adjustments", []))
        msg.append(f"- Follow-up adjustment: {adjustments}")

    user_message = reviewer.get("user_message") or result.get("message")
    if user_message:
        msg.extend(["", user_message])

    msg.extend(
        [
            "",
            "💰 Cost breakdown",
            f"- Flight: {cost_breakdown.get('flight', 'SGD 0')}",
            f"- Hotel: {cost_breakdown.get('hotel', 'SGD 0')}",
            f"- Activities: {cost_breakdown.get('activities', 'SGD 0')}",
            f"- Transport: {cost_breakdown.get('local_transport', 'SGD 0')}",
            f"- Food: {cost_breakdown.get('food', 'SGD 0')}",
            f"- Total: {cost_breakdown.get('total', _format_money(estimated_total))}",
        ]
    )

    flight = travel.get("flight", {}) or {}
    hotel = travel.get("hotel", {}) or {}
    transport = travel.get("transport", {}) or {}

    msg.extend(
        [
            "",
            "✈️ Travel details",
            f"- Flight: {flight.get('suggestion', '-')}",
            f"  Price: {flight.get('estimated_price', '-')}",
        ]
    )

    if flight.get("search_link"):
        msg.append(f"  Search: {flight.get('search_link')}")

    msg.extend(
        [
            "",
            f"- Hotel: {hotel.get('name', '-')}",
            f"  Price: {hotel.get('estimated_price', '-')}",
            f"  Location: {hotel.get('location_note', '-')}",
        ]
    )

    if hotel.get("comfort_note"):
        msg.append(f"  Note: {hotel.get('comfort_note')}")

    if hotel.get("booking_link"):
        msg.append(f"  Booking search: {hotel.get('booking_link')}")

    msg.extend(
        [
            "",
            f"- Local transport: {transport.get('mode', '-')}",
            f"  Cost: {transport.get('estimated_cost', '-')}",
            f"  Notes: {transport.get('notes', '-')}",
        ]
    )

    if daily_itinerary:
        msg.extend(["", "🗓 Day-by-day itinerary"])
        for item in _safe_list(daily_itinerary, 5):
            if isinstance(item, dict):
                msg.append(f"Day {item.get('day', '-')}: {item.get('title', '')}")
                if item.get("details"):
                    msg.append(f"  {item.get('details')}")
            else:
                msg.append(f"- {str(item)}")

    if attractions:
        msg.extend(["", "📍 Nearby attractions"])
        for item in _safe_list(attractions, 3):
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
        msg.extend(["", "🍜 Food & restaurants"])
        for item in _safe_list(restaurants, 3):
            if isinstance(item, dict):
                msg.append(
                    f"- {item.get('name', 'Restaurant')} "
                    f"({item.get('distance_note', 'Not provided')})"
                )
                if item.get("search_link"):
                    msg.append(f"  Search: {item.get('search_link')}")
            else:
                msg.append(f"- {str(item)}")

    alternatives = []
    state = result.get("state", {}) or {}
    for variant in state.get("plan_variants", []) or []:
        if variant.get("variant_key") == selected_variant.get("variant_key"):
            continue

        label = variant.get("variant_label", "Alternative")
        v_ranking = variant.get("ranking", {}) or {}
        pct = v_ranking.get("score_pct")
        total = v_ranking.get("estimated_total")

        if isinstance(pct, (int, float)):
            alternatives.append(f"- {label}: {pct:.0f}% / {_format_money(total)}")

    if alternatives:
        msg.extend(["", "🔁 Other options"])
        msg.extend(alternatives[:2])

    msg.extend(
        [
            "",
            "💬 Try a follow-up:",
            "- cheaper option",
            "- more comfort please",
            "- add more food places",
            "- make it less rushed",
            "- add nature activities",
        ]
    )

    return "\n".join(msg)


async def format_and_send(update: Update):
    global ptb

    text = update.message.text if update.message else ""
    chat_id = update.effective_chat.id

    payload = parse_trip_request(text)
    payload["feedback"] = None

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
            response = await client.post(f"{backend_base}/plan", json=payload)
            response.raise_for_status()
            result = response.json()
    except Exception as exc:
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
            f"Failed to generate trip.\nError: {str(exc)}",
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

    final_message = build_telegram_summary(result, payload)
    print("FINAL MESSAGE:\n", final_message)

    try:
        await send_telegram_message(chat_id, final_message)
    except Exception as exc:
        await send_telegram_message(chat_id, f"Send error: {str(exc)}")


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