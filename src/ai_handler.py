"""
AI Handler — Claude API integration with rate limiting & session management
"""

import asyncio
import logging
import os
import time
from typing import Optional

import anthropic

from session import get_session, save_session, refresh_session_ttl
from system_prompt import FRAMEWORK_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# ── Config ─────────────────────────────────────────────────────
MODEL          = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
MAX_TOKENS     = int(os.getenv("MAX_TOKENS", "4000"))
RATE_LIMIT_SEC = float(os.getenv("RATE_LIMIT_SEC", "3"))   # min seconds between user messages

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ── Simple in-process rate limiter ─────────────────────────────
_last_request: dict[str, float] = {}


def _is_rate_limited(user_id: str) -> bool:
    now = time.time()
    last = _last_request.get(user_id, 0)
    if now - last < RATE_LIMIT_SEC:
        return True
    _last_request[user_id] = now
    return False


def _remaining_cooldown(user_id: str) -> float:
    now = time.time()
    last = _last_request.get(user_id, 0)
    remaining = RATE_LIMIT_SEC - (now - last)
    return max(0.0, remaining)


# ── Main response function ──────────────────────────────────────
async def get_ai_response(user_id: str, user_message: str) -> str:
    """
    Send a message to Claude with the framework system prompt.
    Returns the assistant's reply as a string.
    """
    if _is_rate_limited(user_id):
        secs = _remaining_cooldown(user_id)
        return f"⏳ Tunggu sebentar ({secs:.1f} detik) sebelum mengirim pesan berikutnya."

    messages = get_session(user_id)
    messages.append({"role": "user", "content": user_message})

    try:
        # Run synchronous Claude call in thread pool to keep async loop free
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=FRAMEWORK_SYSTEM_PROMPT,
                messages=messages,
            )
        )

        reply = response.content[0].text
        messages.append({"role": "assistant", "content": reply})
        save_session(user_id, messages)
        refresh_session_ttl(user_id)
        return reply

    except anthropic.RateLimitError:
        logger.warning(f"Claude rate limit hit for user {user_id}")
        return "⚠️ AI sedang sibuk. Coba lagi dalam beberapa detik."

    except anthropic.APIConnectionError:
        logger.error(f"Claude API connection error for user {user_id}")
        return "⚠️ Tidak dapat terhubung ke AI. Periksa koneksi server."

    except anthropic.APIStatusError as e:
        logger.error(f"Claude API status error {e.status_code} for user {user_id}: {e.message}")
        return f"⚠️ Error dari AI ({e.status_code}). Coba lagi."

    except Exception as e:
        logger.exception(f"Unexpected error for user {user_id}: {e}")
        return "⚠️ Terjadi error yang tidak terduga. Coba lagi atau ketik /reset."


# ── Utility: split long text into chunks ───────────────────────
def split_message(text: str, max_len: int = 3800) -> list[str]:
    """
    Split a long message into chunks respecting max_len.
    Tries to split on newlines to avoid mid-sentence cuts.
    """
    if len(text) <= max_len:
        return [text]

    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        # Try to split at last newline within limit
        split_at = text.rfind("\n", 0, max_len)
        if split_at == -1:
            split_at = max_len
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")

    # Add part indicators
    total = len(chunks)
    if total > 1:
        chunks = [f"[{i+1}/{total}]\n{c}" for i, c in enumerate(chunks)]

    return chunks
