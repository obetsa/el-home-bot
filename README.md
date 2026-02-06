# ⚡ Electricity Status Telegram Bot

Telegram bot that monitors electricity availability by pinging a host
and notifies about status changes.

## Features
- 🔋 Electricity ON / 🪫 Electricity OFF notifications
- `/status` — current status and duration
- `/history` — recent status changes
- Environment-based configuration
- Docker-ready

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/el-bot.git
cd el-bot
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
