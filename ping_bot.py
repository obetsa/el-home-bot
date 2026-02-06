import subprocess
import platform
import asyncio
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from telegram import Bot

# ===== ENV =====
load_dotenv(Path(__file__).parent / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
HOST = os.getenv("HOST")

PING_COUNT = int(os.getenv("PING_COUNT", 1))
INTERVAL = int(os.getenv("INTERVAL", 10))
HISTORY_LIMIT = int(os.getenv("HISTORY_LIMIT", 5))

if not BOT_TOKEN or not CHAT_ID or not HOST:
    raise RuntimeError("BOT_TOKEN, CHAT_ID, HOST must be set in .env")

# =================

bot = Bot(token=BOT_TOKEN)

last_status = None
status_since = None
history = []
last_update_id = None


def ping_host(host, count):
    system = platform.system().lower()
    cmd = ["ping", "-n" if system == "windows" else "-c", str(count), host]

    result = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0


def format_duration(seconds):
    minutes, _ = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")

    return " ".join(parts) if parts else "less than 1m"


async def send_message(text):
    await bot.send_message(chat_id=CHAT_ID, text=text)


def status_text(status):
    if status == "ok":
        return "🔋 Electricity ON"
    return "🪫 Electricity OFF"


async def monitor():
    global last_status, status_since, history

    print("Ping monitor started")

    while True:
        now = datetime.now()
        ping_ok = ping_host(HOST, PING_COUNT)
        current_status = "ok" if ping_ok else "bad"

        if current_status != last_status:
            duration = (
                format_duration((now - status_since).total_seconds())
                if status_since else "N/A"
            )

            message = (
                f"⚡ Electricity status changed\n"
                f"From: {status_text(last_status) if last_status else 'N/A'}\n"
                f"Duration: {duration}\n"
                f"To: {status_text(current_status)}"
            )

            await send_message(message)

            history.append(
                f"{now:%d.%m.%Y [%H:%M]} : {status_text(current_status)}\n"
                f"Duration: {duration}"
            )
            history[:] = history[-HISTORY_LIMIT:]

            last_status = current_status
            status_since = now

        if status_since is None:
            status_since = now

        await asyncio.sleep(INTERVAL)


async def command_listener():
    global last_update_id

    print("Command listener started")

    while True:
        updates = await bot.get_updates(offset=last_update_id, timeout=10)

        for update in updates:
            last_update_id = update.update_id + 1

            if not update.message or not update.message.text:
                continue

            if update.message.chat_id != CHAT_ID:
                continue

            text = update.message.text.strip()

            if text == "/status":
                if not last_status:
                    await send_message("Status unknown yet.")
                else:
                    duration = format_duration(
                        (datetime.now() - status_since).total_seconds()
                    )
                    await send_message(
                        f"📊 Current status\n"
                        f"{status_text(last_status)}\n"
                        f"Since: {duration}"
                    )

            elif text == "/history":
                if not history:
                    await send_message("No history yet.")
                else:
                    await send_message(
                        "📜 Status history:\n" + "\n".join(history)
                    )

        await asyncio.sleep(2)


async def main():
    await asyncio.gather(
        monitor(),
        command_listener()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped")
