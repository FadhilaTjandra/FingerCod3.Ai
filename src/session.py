"""
Session Manager — Redis-based conversation history per user
"""

import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Try Redis, fallback to in-memory dict for local dev
try:
    import redis
    _redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
    _redis_client.ping()
    USE_REDIS = True
    logger.info("Redis connected successfully.")
except Exception:
    USE_REDIS = False
    _memory_store: dict = {}
    logger.warning("Redis not available. Using in-memory session store (not persistent).")

SESSION_TTL   = 3600        # 1 hour expiry per session
MAX_MESSAGES  = 20          # max messages kept per session (token control)
SESSION_PREFIX = "fnc_session:"


def _key(user_id: str) -> str:
    return f"{SESSION_PREFIX}{user_id}"


def get_session(user_id: str) -> list:
    """Return message history list for a given user."""
    try:
        if USE_REDIS:
            data = _redis_client.get(_key(user_id))
            return json.loads(data) if data else []
        else:
            return list(_memory_store.get(_key(user_id), []))
    except Exception as e:
        logger.error(f"get_session error for {user_id}: {e}")
        return []


def save_session(user_id: str, messages: list) -> None:
    """Persist message history, keeping only the last MAX_MESSAGES entries."""
    trimmed = messages[-MAX_MESSAGES:]
    try:
        if USE_REDIS:
            _redis_client.setex(_key(user_id), SESSION_TTL, json.dumps(trimmed))
        else:
            _memory_store[_key(user_id)] = trimmed
    except Exception as e:
        logger.error(f"save_session error for {user_id}: {e}")


def clear_session(user_id: str) -> None:
    """Delete session for a user."""
    try:
        if USE_REDIS:
            _redis_client.delete(_key(user_id))
        else:
            _memory_store.pop(_key(user_id), None)
    except Exception as e:
        logger.error(f"clear_session error for {user_id}: {e}")


def session_exists(user_id: str) -> bool:
    """Check if a session exists for the user."""
    try:
        if USE_REDIS:
            return bool(_redis_client.exists(_key(user_id)))
        else:
            return _key(user_id) in _memory_store
    except Exception:
        return False


def refresh_session_ttl(user_id: str) -> None:
    """Reset expiry timer on an existing session."""
    try:
        if USE_REDIS:
            _redis_client.expire(_key(user_id), SESSION_TTL)
    except Exception as e:
        logger.error(f"refresh_session_ttl error for {user_id}: {e}")
