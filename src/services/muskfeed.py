import random
import datetime
import requests
from zoneinfo import ZoneInfo
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import ConflictingIdError

from src.config.settings import NEWS_CHAT_ID

TZ = ZoneInfo("America/Los_Angeles")

MUSK_QUOTES = [
    "If you need inspiring words, don't do it.",
    "Persistence beats luck. Usually.",
    "Falcon 1 failed three times. The 4th changed everything.",
    "Optimism. Pisses off pessimists.",
]

NEURALINK = [
    "Neuralink: trial expanding; longer stable cursor sessions.",
    "Neuralink: R1 robot faster craniotomy cycle.",
    "Neuralink: early wrist-intent decoding looks promising.",
    "Neuralink: stable thought-typing, drift improved.",
]

def spacex_next_launch_short() -> str:
    try:
        r = requests.get("https://api.spacexdata.com/v5/launches/next", timeout=8)
        r.raise_for_status()
        j = r.json()
        name = j.get("name") or "SpaceX launch"
        t0_iso = j.get("date_utc")
        t0 = datetime.datetime.fromisoformat(t0_iso.replace("Z", "+00:00")) if t0_iso else None
        t0_pt = t0.astimezone(TZ).strftime("%Y-%m-%d %H:%M") if t0 else "—"
        return f"{name} · {t0_pt} PT"
    except Exception:
        return "Starlink window · — PT"

def one_news_line() -> str:
    return f"🧠 {random.choice(NEURALINK)}\\n🚀 {spacex_next_launch_short()}\\n🧨 {random.choice(MUSK_QUOTES)}"

def post_news(bot, chat_id: int):
    bot.send_message(chat_id, one_news_line())

def setup_scheduler(bot, logger):
    scheduler = BackgroundScheduler(timezone=TZ)
    
    try:
        scheduler.add_job(lambda: NEWS_CHAT_ID and post_news(bot, int(NEWS_CHAT_ID)),
                          "cron", hour=14, minute=0, id="nf14", replace_existing=True)
        scheduler.add_job(lambda: NEWS_CHAT_ID and post_news(bot, int(NEWS_CHAT_ID)),
                          "cron", hour=20, minute=0, id="nf20", replace_existing=True)
        scheduler.start()
        logger.info("Muskfeed scheduled at 14:00 & 20:00 PT")
    except ConflictingIdError:
        logger.warning("Jobs already exist, replacing")
    except Exception as e:
        logger.error(f"Scheduler failed: {e}")
