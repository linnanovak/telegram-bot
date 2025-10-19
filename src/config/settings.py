import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "YOUR_USERNAME")
NEWS_CHAT_ID = os.getenv("NEWS_CHAT_ID")
NEWS_CHANNEL_USERNAME = os.getenv("NEWS_CHANNEL_USERNAME", "")

if not BOT_TOKEN:
    raise SystemExit("Нет BOT_TOKEN в .env")
