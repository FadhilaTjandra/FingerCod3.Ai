"""
Main Entry Point — Framework Universal Niche V1.5 Bot
Build by Fingercod3

Runs Telegram and Discord bots concurrently in separate threads.
"""

import logging
import os
import sys
import threading

from dotenv import load_dotenv

# Load .env before importing bot modules
load_dotenv()

# ── Logging setup ───────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("main")

# ── Import bots ─────────────────────────────────────────────────
from telegram_bot import run_telegram
from discord_bot  import run_discord


def _run_in_thread(target_fn, name: str) -> threading.Thread:
    t = threading.Thread(target=target_fn, name=name, daemon=True)
    t.start()
    return t


def main():
    logger.info("=" * 60)
    logger.info("  FRAMEWORK UNIVERSAL NICHE V1.5 — Build by Fingercod3")
    logger.info("=" * 60)

    # Determine which bots to run
    run_tg  = bool(os.getenv("TELEGRAM_TOKEN"))
    run_dc  = bool(os.getenv("DISCORD_TOKEN"))

    if not run_tg and not run_dc:
        logger.error(
            "No bot tokens configured. "
            "Set TELEGRAM_TOKEN and/or DISCORD_TOKEN in your .env file."
        )
        sys.exit(1)

    threads = []

    if run_tg:
        logger.info("Starting Telegram bot...")
        threads.append(_run_in_thread(run_telegram, "TelegramBot"))

    if run_dc:
        logger.info("Starting Discord bot...")
        threads.append(_run_in_thread(run_discord, "DiscordBot"))

    logger.info(f"{len(threads)} bot(s) running. Press Ctrl+C to stop.")

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        logger.info("Shutting down. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
