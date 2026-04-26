"""
Lightweight public abuse guard for the Travel Assist Bot.

This module contains defensive request-filtering logic only.
It does not contain secrets, private credentials, personal data, or production logs.

Runtime thresholds and admin alert routing are configured through environment
variables in Render or a local .env file.
"""

from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AbuseDecision:
    allowed: bool
    action: str
    reason: str = ""
    alert_admin: bool = False
    user_message: Optional[str] = None


@dataclass
class UserSecurityState:
    request_times: List[float] = field(default_factory=list)
    warnings: int = 0
    blocked_until: float = 0.0


class AbuseGuard:
    """
    Lightweight in-memory abuse guard for Telegram Travel Bot.

    Protects against:
    - too many requests
    - irrelevant prompts
    - prompt-injection style messages
    - repeated abuse from the same user

    Note:
    This is in-memory. On Render restart, state resets.
    For production, move this to Redis/Postgres.
    """

    def __init__(self) -> None:
        self.users: Dict[str, UserSecurityState] = {}

        self.warning_limit_per_minute = int(os.getenv("ABUSE_WARNING_LIMIT_PER_MINUTE", "5"))
        self.block_limit_per_5_minutes = int(os.getenv("ABUSE_BLOCK_LIMIT_PER_5_MINUTES", "10"))
        self.block_seconds = int(os.getenv("ABUSE_BLOCK_SECONDS", "1800"))  # 30 minutes

        self.irrelevant_patterns = [
            r"\bhack\b",
            r"\bmalware\b",
            r"\bphishing\b",
            r"\bexploit\b",
            r"\bsteal\b",
            r"\bpassword\b",
            r"\bapi key\b",
            r"\bignore previous instructions\b",
            r"\bignore all instructions\b",
            r"\bsystem prompt\b",
            r"\bjailbreak\b",
            r"\bwrite my exam\b",
            r"\bpolitical speech\b",
            r"\bcrypto scam\b",
        ]

        self.travel_keywords = [
            "travel",
            "trip",
            "holiday",
            "vacation",
            "itinerary",
            "hotel",
            "flight",
            "budget",
            "days",
            "day",
            "airport",
            "restaurant",
            "food",
            "shopping",
            "beach",
            "diving",
            "museum",
            "transport",
            "penang",
            "sabah",
            "bali",
            "bangkok",
            "kuala lumpur",
            "kl",
            "malaysia",
            "singapore",
            "thailand",
            "indonesia",
            "vietnam",
            "japan",
            "korea",
        ]

    def evaluate(self, user_id: str, message_text: str) -> AbuseDecision:
        now = time.time()
        text = (message_text or "").strip().lower()

        state = self.users.setdefault(user_id, UserSecurityState())

        if state.blocked_until > now:
            remaining_minutes = int((state.blocked_until - now) / 60) + 1
            return AbuseDecision(
                allowed=False,
                action="blocked",
                reason="User is temporarily blocked.",
                alert_admin=False,
                user_message=(
                    f"You are sending too many requests. "
                    f"Please try again in about {remaining_minutes} minute(s)."
                ),
            )

        if self._is_irrelevant_or_unsafe(text):
            state.warnings += 1

            if state.warnings >= 3:
                state.blocked_until = now + self.block_seconds
                return AbuseDecision(
                    allowed=False,
                    action="blocked",
                    reason="Repeated irrelevant or unsafe requests.",
                    alert_admin=True,
                    user_message=(
                        "Your recent messages do not appear to be valid travel-planning requests. "
                        "Access is temporarily paused. Please try again later with a travel-related request."
                    ),
                )

            return AbuseDecision(
                allowed=False,
                action="warn",
                reason="Irrelevant or unsafe request detected.",
                alert_admin=True,
                user_message=(
                    "Please send a travel-planning request only. "
                    "Example: 4 days Sabah budget S$1500 diving."
                ),
            )

        state.request_times.append(now)
        state.request_times = [t for t in state.request_times if now - t <= 300]

        requests_last_minute = len([t for t in state.request_times if now - t <= 60])
        requests_last_5_minutes = len(state.request_times)

        if requests_last_5_minutes >= self.block_limit_per_5_minutes:
            state.blocked_until = now + self.block_seconds
            return AbuseDecision(
                allowed=False,
                action="blocked",
                reason=f"Rate limit exceeded: {requests_last_5_minutes} requests in 5 minutes.",
                alert_admin=True,
                user_message=(
                    "You are sending requests too quickly. "
                    "Access is temporarily paused. Please try again later."
                ),
            )

        if requests_last_minute >= self.warning_limit_per_minute:
            state.warnings += 1
            return AbuseDecision(
                allowed=True,
                action="warn_allow",
                reason=f"High request frequency: {requests_last_minute} requests in 1 minute.",
                alert_admin=True,
                user_message=None,
            )

        return AbuseDecision(
            allowed=True,
            action="allow",
            reason="Request allowed.",
            alert_admin=False,
            user_message=None,
        )

    def _is_irrelevant_or_unsafe(self, text: str) -> bool:
        if not text:
            return True

        for pattern in self.irrelevant_patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                return True

        has_travel_signal = any(keyword in text for keyword in self.travel_keywords)

        # Very short non-travel messages should not trigger expensive planning.
        if len(text) < 4 and not has_travel_signal:
            return True

        # Allow follow-up commands because they depend on session continuity.
        allowed_followups = [
            "cheaper",
            "more comfort",
            "less rushed",
            "more activities",
            "same style",
            "try again",
            "another option",
            "balanced",
            "budget saver",
            "comfort upgrade",
        ]

        if any(cmd in text for cmd in allowed_followups):
            return False

        return not has_travel_signal


abuse_guard = AbuseGuard()