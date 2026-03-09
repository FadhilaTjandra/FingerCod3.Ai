"""
Discord Bot — Framework Universal Niche V1.5
Build by Fingercod3
"""

import logging
import os

import discord

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

ALLOWED_GUILD_IDS   = _parse_ids("ALLOWED_GUILD_IDS")
ALLOWED_CHANNEL_IDS = _parse_ids("ALLOWED_CHANNEL_IDS")  # optional: restrict to specific channels
BOT_PREFIX          = os.getenv("DISCORD_PREFIX", "!")

DISCORD_MAX_LEN = 1900  # safe under Discord's 2000 char limit


def _is_allowed_guild(guild_id: int) -> bool:
    if not ALLOWED_GUILD_IDS:
        return True  # open if no restriction set
    return guild_id in ALLOWED_GUILD_IDS


def _is_allowed_channel(channel_id: int) -> bool:
    if not ALLOWED_CHANNEL_IDS:
        return True  # open if no restriction set
    return channel_id in ALLOWED_CHANNEL_IDS


# ── Bot ────────────────────────────────────────────────────────
class FrameworkBot(discord.Client):

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

    async def on_ready(self):
        logger.info(f"Discord bot logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="START | Framework V1.5"
            )
        )

    async def on_message(self, message: discord.Message):
        # Ignore own messages and other bots
        if message.author.bot:
            return

        # Guild-level check
        if message.guild and not _is_allowed_guild(message.guild.id):
            return

        # Channel-level check
        if not _is_allowed_channel(message.channel.id):
            return

        user_id = str(message.author.id)
        content  = message.content.strip()

        if not content:
            return

        # ── Built-in commands ──────────────────────────────────
        if content.lower() in (f"{BOT_PREFIX}reset", "!reset", "/reset"):
            clear_session(user_id)
            await message.reply(
                "✅ Sesi berhasil direset.\n"
                "Ketik **START** atau **MULAI** untuk mulai lagi."
            )
            return

        if content.lower() in (f"{BOT_PREFIX}help", "!help", "/help"):
            await message.reply(
                "📋 **BANTUAN FRAMEWORK BOT**\n\n"
                "**Memulai:** Ketik `START` atau `MULAI`\n\n"
                "**Perintah Iterasi:**\n"
                "`REVISI STAGE [N]` — Revisi stage tertentu\n"
                "`GANTI ANGLE` — Ganti angle kamera\n"
                "`GANTI STYLE` — Ganti style karakter\n"
                "`GANTI LOKASI` — Ganti setting/lokasi\n"
                "`TAMBAH STAGE` — Tambah stage baru\n"
                "`GANTI CINEMATIC` — Ganti cinematic A/B/C\n"
                "`GANTI FORMAT` — Ganti TEXT/JSON\n"
                "`GANTI TIMELAPSE` — Ganti gaya timelapse\n"
                "`AKTIFKAN LED` — Aktifkan LED mode\n"
                "`ULANG SEMUA` — Generate ulang dari awal\n\n"
                "**Bot Commands:**\n"
                "`!reset` — Reset sesi\n"
                "`!help`  — Tampilkan bantuan\n"
                "`!status` — Cek status sesi"
            )
            return

        if content.lower() in (f"{BOT_PREFIX}status", "!status", "/status"):
            has_session = session_exists(user_id)
            await message.reply(
                f"📊 **Status Sesi**\n\n"
                f"User ID: `{user_id}`\n"
                f"Sesi aktif: {'✅ Ya' if has_session else '❌ Tidak'}"
            )
            return

        # ── AI response ────────────────────────────────────────
        async with message.channel.typing():
            reply = await get_ai_response(user_id, content)
            parts = split_message(reply, max_len=DISCORD_MAX_LEN)

            first = True
            for part in parts:
                if first:
                    await message.reply(part)
                    first = False
                else:
                    await message.channel.send(part)

    async def on_error(self, event: str, *args, **kwargs):
        logger.exception(f"Discord error in {event}")


# ── Runner ──────────────────────────────────────────────────────
def run_discord() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN not set. Discord bot will not start.")
        return

    bot = FrameworkBot()
    logger.info("Discord bot starting...")
    bot.run(token)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_discord()
