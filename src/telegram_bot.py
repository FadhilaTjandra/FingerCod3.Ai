"""
Telegram Bot — Framework Universal Niche V1.5
Build by Fingercod3
"""

import logging
import os

from telegram import Update, BotCommand
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from ai_handler import get_ai_response, split_message
from session import clear_session, session_exists

logger = logging.getLogger(__name__)

# ── Access control ─────────────────────────────────────────────
def _parse_ids(env_key: str) -> set[int]:
    raw = os.getenv(env_key, "")
    result = set()
    for part in raw.split(","):
        part = part.strip()
        if part:
            try:
                result.add(int(part))
            except ValueError:
                logger.warning(f"Invalid ID in {env_key}: {part}")
    return result

ALLOWED_GROUP_IDS = _parse_ids("ALLOWED_GROUP_IDS")
ALLOWED_USER_IDS  = _parse_ids("ALLOWED_USER_IDS")   # optional: whitelist specific users


def _is_allowed(chat_id: int, user_id: int) -> bool:
    """Allow if: no restrictions set (open), OR chat/user is whitelisted."""
    if not ALLOWED_GROUP_IDS and not ALLOWED_USER_IDS:
        return True  # no restriction configured — open to all
    if chat_id in ALLOWED_GROUP_IDS:
        return True
    if user_id in ALLOWED_USER_IDS:
        return True
    return False


# ── Helpers ────────────────────────────────────────────────────
async def _send_long(update: Update, text: str, max_len: int = 3800) -> None:
    """Send potentially long text, splitting if necessary."""
    parts = split_message(text, max_len)
    for part in parts:
        await update.message.reply_text(part)


# ── Command handlers ───────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    clear_session(user_id)
    await update.message.reply_text(
        "🎬 *FRAMEWORK UNIVERSAL NICHE V1.5*\n"
        "_Build by Fingercod3_\n\n"
        "Ketik *START* atau *MULAI* untuk memulai sesi baru.\n\n"
        "Perintah tersedia:\n"
        "/reset — Reset sesi\n"
        "/help  — Bantuan",
        parse_mode="Markdown",
    )


async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    clear_session(user_id)
    await update.message.reply_text(
        "✅ Sesi berhasil direset.\nKetik *START* atau *MULAI* untuk mulai lagi.",
        parse_mode="Markdown",
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📋 *BANTUAN FRAMEWORK BOT*\n\n"
        "*Memulai:*\n"
        "  Ketik `START` atau `MULAI`\n\n"
        "*Perintah Iterasi:*\n"
        "  `REVISI STAGE [N]` — Revisi stage tertentu\n"
        "  `GANTI ANGLE` — Ganti angle kamera\n"
        "  `GANTI STYLE` — Ganti style karakter\n"
        "  `GANTI LOKASI` — Ganti lokasi\n"
        "  `TAMBAH STAGE` — Tambah stage baru\n"
        "  `GANTI CINEMATIC` — Ganti cinematic A/B/C\n"
        "  `GANTI FORMAT` — Ganti TEXT/JSON\n"
        "  `GANTI TIMELAPSE` — Ganti gaya timelapse\n"
        "  `AKTIFKAN LED` — Aktifkan LED mode\n"
        "  `ULANG SEMUA` — Reset & generate ulang\n\n"
        "*Commands:*\n"
        "  /start — Mulai bot\n"
        "  /reset — Reset sesi\n"
        "  /help  — Tampilkan bantuan ini",
        parse_mode="Markdown",
    )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    has_session = session_exists(user_id)
    await update.message.reply_text(
        f"📊 *Status Sesi*\n\n"
        f"User ID: `{user_id}`\n"
        f"Sesi aktif: {'✅ Ya' if has_session else '❌ Tidak'}",
        parse_mode="Markdown",
    )


# ── Message handler ────────────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if not _is_allowed(chat_id, user_id):
        # Silently ignore unauthorized chats
        return

    text = update.message.text.strip()
    uid  = str(user_id)

    # Show typing indicator
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    reply = await get_ai_response(uid, text)
    await _send_long(update, reply)


# ── Error handler ───────────────────────────────────────────────
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Telegram error: {context.error}", exc_info=context.error)


# ── Runner ──────────────────────────────────────────────────────
def run_telegram() -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("TELEGRAM_TOKEN not set. Telegram bot will not start.")
        return

    app = Application.builder().token(token).build()

    # Commands
    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("reset",  cmd_reset))
    app.add_handler(CommandHandler("help",   cmd_help))
    app.add_handler(CommandHandler("status", cmd_status))

    # Messages
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    # Errors
    app.add_error_handler(error_handler)

    logger.info("Telegram bot started.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_telegram()
