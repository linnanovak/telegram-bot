# bot.py — Ash: portfolio-grade Telegram bot (RU/EN, Catalog, Tips, Muskfeed)
# deps: pyTelegramBotAPI, python-dotenv, APScheduler, requests
# pip install pyTelegramBotAPI python-dotenv APScheduler requests

import os
import json
import random
import datetime
import logging
from pathlib import Path
from zoneinfo import ZoneInfo
from time import time
import requests
import telebot
from telebot import types
from telebot.types import BotCommand, BotCommandScopeChat

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import ConflictingIdError
from dotenv import load_dotenv

# =========================
# ENV & BASE
# =========================
load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "YOUR_USERNAME")
NEWS_CHAT_ID = os.getenv("NEWS_CHAT_ID")
NEWS_CHANNEL_USERNAME = os.getenv("NEWS_CHANNEL_USERNAME", "")

if not BOT_TOKEN:
    raise SystemExit("Нет BOT_TOKEN в .env")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
TZ = ZoneInfo("America/Los_Angeles")

# =========================
# LOGGING
# =========================
logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("ash")
user_logger = logging.getLogger("user_logger")
user_logger.setLevel(logging.INFO)
fh = logging.FileHandler("users.log", encoding="utf-8")
fh.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
user_logger.addHandler(fh)

def log_user_info(m):
    txt = f"ID:{m.from_user.id} | name:{m.from_user.first_name} | text:{(m.text or '').strip()}"
    user_logger.info(txt)

# =========================
# STATE: user language
# =========================
USER_LANG_FILE = "user_lang.json"
user_langs = {}

def load_user_langs():
    global user_langs
    try:
        with open(USER_LANG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            user_langs = {int(k): ("ru" if v == "ru" else "en") for k, v in data.items()}
    except FileNotFoundError:
        user_langs = {}
    except Exception as e:
        logger.error(f"Failed to load user_langs: {e}")
        user_langs = {}

def save_user_langs():
    try:
        with open(USER_LANG_FILE, "w", encoding="utf-8") as f:
            json.dump(user_langs, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save user_langs: {e}")

def set_lang(user_id: int, lang: str):
    user_langs[user_id] = "ru" if lang == "ru" else "en"
    save_user_langs()

def get_lang(user_id: int) -> str:
    return user_langs.get(user_id, "en")

load_user_langs()

# =========================
# TEXTS (RU/EN)
# =========================
ABOUT_RU = (
    "Собран на Python 3\nМодульная архитектура\nУстойчив к нагрузкам. Масштабируем\n"
    "Встроенные: логирование, планировщик, двуязычный режим\n"
    "Функции: интеграция с каналом, обработка пользователей, задачи по расписанию\n"
    "Аптайм: 24/7."
)

ABOUT_EN = (
    "Built on Python 3\nModular architecture\nLoad-resistant. Scalable\n"
    "Embedded: logging, scheduler, bilingual mode\n"
    "Functions: channel integration, user processing, scheduled tasks\n"
    "Uptime: 24/7"
)

MSG = {
    "ru": {
        "start": "Выбери язык / Choose your language",
        "status": "я здесь",
        "welcome": (
            "зови меня Аш. я не про вежливость, я про результат 🔥\n"
            "телеграм-бот может быть быстрым, умным и с характером.\n"
            "говорю на двух языках, веду новостной канал — и всё, что захочешь.\n"
            "стабильность? 24/7. я говорю меньше, чем делаю."
        ),
        "menu": "Меню:",
        "pick_lang": "Выбери язык:",
        "catalog_title": "Catalog — боты, которые действительно работают.",
        "catalog_btn_simple": "Simple",
        "catalog_btn_simple_custom": "Simple Custom (this bot)",
        "catalog_btn_integrations": "Custom integrations",
        "catalog_btn_ai_ultra": "AI-powered Ultra",
        "catalog_btn_sale": "Акции",
        "catalog_btn_contact": "Contact",
        "card_simple": "Базовый Telegram-бот: команды, ответы, простая логика.\nПодходит для быстрых MVP и мини-сервисов.",
        "card_simple_custom": "Кастом на Python (как этот бот): канал-постинг, двуязычие, планировщик, логи.\nБез конструкторов — чистый код.",
        "card_integrations": "Интеграции: Google Sheets/API, webhooks, формы/лиды, нестандартные сценарии.\nАрхитектура под проект.",
        "card_ai_ultra": "Диалоги на ИИ, память, персонализация, сложные ветки.\nПремиум-уровень, по брифу.",
        "sale": "Временная акция: Simple Custom — $300 для первых 5. Потом — стандартные ставки.",
        "channel_here": "Канал",
        "one_news_intro": "Одна на вкус:",
        "go_channel": "Перейти в канал",
        "tip_title": "Поддержать Ash",
        "tip_desc": "Throw a star my way ✨",
        "tip_btn_1": "☕ Coffee",
        "tip_btn_2": "🍕 Pizza",
        "tip_btn_3": "🔥 Big Support",
        "thanks_tip": "Спасибо за поддержку. Зачтено. 🔥",
        "about": ABOUT_RU,
        "prev": "◀ Пред",
        "back_catalog": "Каталог",
        "next": "Дальше ▶",
        "back_main": "Главное меню",
        "back_to": "Назад"
    },
    "en": {
        "start": "Choose your language 👇",
        "status": "online",
        "welcome": (
            "call me Ash. I'm not about etiquette — I'm about outcomes.\n"
            "a Telegram bot can be fast, sharp, and with attitude.\n"
            "bilingual, runs a news channel — and whatever you need.\n"
            "uptime? 24/7. I talk less than I ship."
        ),
        "menu": "Menu:",
        "pick_lang": "Choose language:",
        "catalog_title": "Catalog — bots that actually work.",
        "catalog_btn_simple": "Simple",
        "catalog_btn_simple_custom": "Simple Custom (this bot)",
        "catalog_btn_integrations": "Custom integrations",
        "catalog_btn_ai_ultra": "AI-powered Ultra",
        "catalog_btn_sale": "Promo",
        "catalog_btn_contact": "Contact",
        "card_simple": "Basic Telegram bot: commands, replies, simple logic.\nGreat for quick MVPs and mini-services.",
        "card_simple_custom": "Custom Python build (like this one): channel posting, bilingual, scheduler, logging.\nNo templates — clean code.",
        "card_integrations": "Integrations: Google Sheets/API, webhooks, forms/leads, custom flows.\nArchitecture tailored to your project.",
        "card_ai_ultra": "AI dialogues, memory, personalization, complex flows.\nPremium level, built to brief.",
        "sale": "Launch promo: Simple Custom — $300 for the first 5. Standard rates afterward.",
        "channel_here": "Channel",
        "one_news_intro": "One to taste:",
        "go_channel": "Go to channel",
        "tip_title": "Support Ash",
        "tip_desc": "Throw a star my way ✨",
        "tip_btn_1": "☕ Coffee",
        "tip_btn_2": "🍕 Pizza",
        "tip_btn_3": "🔥 Big Support",
        "thanks_tip": "Thanks for the support. Noted. 🔥",
        "about": ABOUT_EN,
        "prev": "◀ Prev",
        "back_catalog": "Catalog",
        "next": "Next ▶",
        "back_main": "Main menu",
        "back_to": "Back"
    }
}

# =========================
# HELPERS
# =========================
def L(user_id: int, key: str) -> str:
    lang = get_lang(user_id)
    return MSG["ru" if lang == "ru" else "en"][key]

def apply_commands(chat_id: int, lang: str):
    if lang == "ru":
        cmds = [
            BotCommand("start", "старт / выбор языка"),
            BotCommand("status", "пульс"),
            BotCommand("channel", "канал"),
            BotCommand("news_now", "новость сейчас"),
            BotCommand("catalog", "каталог"),
            BotCommand("tip", "поддержать ⭐"),
            BotCommand("language", "язык"),
            BotCommand("about", "обо мне"),
        ]
    else:
        cmds = [
            BotCommand("start", "start / choose language"),
            BotCommand("status", "status"),
            BotCommand("channel", "channel"),
            BotCommand("news_now", "news now"),
            BotCommand("catalog", "catalog"),
            BotCommand("tip", "tip ⭐"),
            BotCommand("language", "language"),
            BotCommand("about", "about"),
        ]
    scope = BotCommandScopeChat(chat_id)
    bot.set_my_commands(cmds, scope=scope)

def build_main_menu(user_id: int) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=2)
    lang = get_lang(user_id)
    
    if lang == "ru":
        kb.add(
            types.InlineKeyboardButton("Статус", callback_data="m:status"),
            types.InlineKeyboardButton("Канал", callback_data="m:channel"),
        )
        kb.add(
            types.InlineKeyboardButton("Новости", callback_data="m:news"),
            types.InlineKeyboardButton("Каталог", callback_data="m:catalog"),
        )
        kb.add(
            types.InlineKeyboardButton("Язык", callback_data="m:language"),
            types.InlineKeyboardButton("Обо мне", callback_data="m:about"),
        )
        kb.add(types.InlineKeyboardButton("Поддержать ⭐", callback_data="m:tip"))
    else:
        kb.add(
            types.InlineKeyboardButton("Status", callback_data="m:status"),
            types.InlineKeyboardButton("Channel", callback_data="m:channel"),
        )
        kb.add(
            types.InlineKeyboardButton("News", callback_data="m:news"),
            types.InlineKeyboardButton("Catalog", callback_data="m:catalog"),
        )
        kb.add(
            types.InlineKeyboardButton("Language", callback_data="m:language"),
            types.InlineKeyboardButton("About", callback_data="m:about"),
        )
        kb.add(types.InlineKeyboardButton("Tip ⭐", callback_data="m:tip"))
    
    return kb

def build_catalog_keyboard(user_id: int) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton(L(user_id, "back_main"), callback_data="m:main"))
    kb.add(
        types.InlineKeyboardButton(L(user_id, "catalog_btn_simple"), callback_data="pkg:simple"),
        types.InlineKeyboardButton(L(user_id, "catalog_btn_simple_custom"), callback_data="pkg:simple_custom"),
        types.InlineKeyboardButton(L(user_id, "catalog_btn_integrations"), callback_data="pkg:integrations"),
        types.InlineKeyboardButton(L(user_id, "catalog_btn_ai_ultra"), callback_data="pkg:ai_ultra"),
    )
    kb.add(types.InlineKeyboardButton(L(user_id, "catalog_btn_sale"), callback_data="promo:sale"))
    kb.add(types.InlineKeyboardButton(L(user_id, "catalog_btn_contact"), url=f"https://t.me/{OWNER_USERNAME}"))
    return kb

def channel_link() -> str:
    if NEWS_CHANNEL_USERNAME:
        return f"https://t.me/{NEWS_CHANNEL_USERNAME}"
    if NEWS_CHAT_ID:
        try:
            link = bot.create_chat_invite_link(int(NEWS_CHAT_ID), name="bot-channel-link")
            return link.invite_link
        except Exception:
            return ""
    return ""

def back_to_main_kb(user_id: int) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(L(user_id, "back_main"), callback_data="m:main"))
    return kb

# =========================
# MUSKFEED (one-liner news)
# =========================
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
    return f"🧠 {random.choice(NEURALINK)}\n🚀 {spacex_next_launch_short()}\n🧨 {random.choice(MUSK_QUOTES)}"


# SCHEDULER

scheduler = BackgroundScheduler(timezone=TZ)

def post_news(chat_id: int):
    bot.send_message(chat_id, one_news_line())

def schedule_daily():
    try:
        scheduler.add_job(lambda: NEWS_CHAT_ID and post_news(int(NEWS_CHAT_ID)),
                          "cron", hour=14, minute=0, id="nf14", replace_existing=True)
        scheduler.add_job(lambda: NEWS_CHAT_ID and post_news(int(NEWS_CHAT_ID)),
                          "cron", hour=20, minute=0, id="nf20", replace_existing=True)
        logger.info("Muskfeed scheduled at 14:00 & 20:00 PT")
    except ConflictingIdError:
        logger.warning("Jobs already exist, replacing")

# =========================
# START + LANGUAGE
# =========================
@bot.message_handler(commands=["start"])
def cmd_start(m):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("RU", callback_data="lang:ru"),
        types.InlineKeyboardButton("EN", callback_data="lang:en"),
    )
    bot.send_message(m.chat.id, L(m.from_user.id, "start"), reply_markup=kb)
    
@bot.message_handler(commands=["language"])
def cmd_language(m):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("RU", callback_data="lang:ru"),
        types.InlineKeyboardButton("EN", callback_data="lang:en"),
    )
    bot.send_message(m.chat.id, L(m.from_user.id, "pick_lang"), reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("lang:"))
def on_lang(c: types.CallbackQuery):
    bot.answer_callback_query(c.id)
    lang = c.data.split(":", 1)[1]
    set_lang(c.from_user.id, lang)
    apply_commands(c.message.chat.id, lang)
    
    text = L(c.from_user.id, "welcome")
    kb = build_main_menu(c.from_user.id)
    
    try:
        bot.edit_message_text(
            text,
            chat_id=c.message.chat.id,
            message_id=c.message.message_id,
            reply_markup=kb
        )
    except Exception:
        bot.send_message(c.message.chat.id, text, reply_markup=kb)

# =========================
# CORE COMMANDS
# =========================
@bot.message_handler(commands=["status"])
def cmd_status(m):
    bot.send_message(m.chat.id, L(m.from_user.id, "status"))

@bot.message_handler(commands=["channel"])
def cmd_channel(m):
    url = channel_link()
    if url:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(L(m.from_user.id, "channel_here"), url=url))
        bot.send_message(m.chat.id, L(m.from_user.id, "channel_here"), reply_markup=kb, disable_web_page_preview=True)
    else:
        bot.send_message(m.chat.id, "Channel link is not configured.")

@bot.message_handler(commands=["news_now"])
def cmd_news_now(m):
    url = channel_link()
    text = f"{L(m.from_user.id, 'one_news_intro')}\n\n{one_news_line()}"
    if url:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(L(m.from_user.id, "go_channel"), url=url))
        bot.send_message(m.chat.id, text, reply_markup=kb, disable_web_page_preview=True)
    else:
        bot.send_message(m.chat.id, text)

@bot.message_handler(commands=["menu"])
def cmd_menu(m):
    bot.send_message(m.chat.id, L(m.from_user.id, "welcome"), reply_markup=build_main_menu(m.from_user.id))

# =========================
# CATALOG
# =========================
PACKAGE_ORDER = ["simple", "simple_custom", "integrations", "ai_ultra"]

def _catalog_grid_kb(user_id: int) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton(L(user_id, "back_main"), callback_data="m:main"))
    kb.add(
        types.InlineKeyboardButton(L(user_id, "catalog_btn_simple"), callback_data="pkg:simple"),
        types.InlineKeyboardButton(L(user_id, "catalog_btn_simple_custom"), callback_data="pkg:simple_custom"),
        types.InlineKeyboardButton(L(user_id, "catalog_btn_integrations"), callback_data="pkg:integrations"),
        types.InlineKeyboardButton(L(user_id, "catalog_btn_ai_ultra"), callback_data="pkg:ai_ultra"),
    )
    kb.add(types.InlineKeyboardButton(L(user_id, "catalog_btn_sale"), callback_data="promo:sale"))
    kb.add(types.InlineKeyboardButton(L(user_id, "catalog_btn_contact"), url=f"https://t.me/{OWNER_USERNAME}"))
    return kb

def _catalog_detail_text(user_id: int, key: str) -> str:
    lang = "ru" if get_lang(user_id) == "ru" else "en"
    mapping = {
        "simple": MSG[lang]["card_simple"],
        "simple_custom": MSG[lang]["card_simple_custom"],
        "integrations": MSG[lang]["card_integrations"],
        "ai_ultra": MSG[lang]["card_ai_ultra"],
    }
    return mapping.get(key, "…")

def _catalog_detail_kb(user_id: int, current_key: str) -> types.InlineKeyboardMarkup:
    i = PACKAGE_ORDER.index(current_key)
    prev_key = PACKAGE_ORDER[(i - 1) % len(PACKAGE_ORDER)]
    next_key = PACKAGE_ORDER[(i + 1) % len(PACKAGE_ORDER)]

    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton(L(user_id, "prev"), callback_data=f"pkg:{prev_key}"),
        types.InlineKeyboardButton(L(user_id, "back_catalog"), callback_data="nav:back"),
        types.InlineKeyboardButton(L(user_id, "next"), callback_data=f"pkg:{next_key}"),
    )
    kb.add(types.InlineKeyboardButton(L(user_id, "back_main"), callback_data="m:main"))
    kb.add(types.InlineKeyboardButton(L(user_id, "catalog_btn_contact"), url=f"https://t.me/{OWNER_USERNAME}"))
    return kb

@bot.message_handler(commands=["catalog"])
def cmd_catalog(m):
    if get_lang(m.from_user.id) not in ("ru", "en"):
        set_lang(m.from_user.id, "en")
    bot.send_message(m.chat.id, L(m.from_user.id, "catalog_title"), reply_markup=_catalog_grid_kb(m.from_user.id))

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith(("pkg:", "promo:", "nav:")))
def on_catalog_click(c: types.CallbackQuery):
    uid = c.from_user.id
    data = c.data

    try:
        if data.startswith("pkg:"):
            key = data.split(":", 1)[1]
            text = _catalog_detail_text(uid, key)
            kb = _catalog_detail_kb(uid, key)
            bot.edit_message_text(
                text,
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                reply_markup=kb,
                disable_web_page_preview=True
            )
        elif data == "nav:back":
            bot.edit_message_text(
                L(uid, "catalog_title"),
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                reply_markup=_catalog_grid_kb(uid)
            )
        elif data == "promo:sale":
            txt = MSG["ru"]["sale"] if get_lang(uid) == "ru" else MSG["en"]["sale"]
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton(L(uid, "back_catalog"), callback_data="nav:back"))
            kb.add(types.InlineKeyboardButton(L(uid, "back_main"), callback_data="m:main"))
            kb.add(types.InlineKeyboardButton(L(uid, "catalog_btn_contact"), url=f"https://t.me/{OWNER_USERNAME}"))
            bot.edit_message_text(
                txt,
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                reply_markup=kb,
                disable_web_page_preview=True
            )
    except Exception as e:
        logger.error(f"Catalog error: {e}")
        bot.answer_callback_query(c.id, "Error, try again")

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("m:"))
def on_menu_click(c: types.CallbackQuery):
    user_id = c.from_user.id
    action = c.data.split(":", 1)[1]
    
    bot.answer_callback_query(c.id)
    
    if action == "status":
        text = L(user_id, "status")
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(L(user_id, "back_main"), callback_data="m:main"))
        bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=kb)
    
    elif action == "channel":
        url = channel_link()
        text = L(user_id, "channel_here")
        kb = types.InlineKeyboardMarkup()
        if url:
            kb.add(types.InlineKeyboardButton(L(user_id, "go_channel"), url=url))
        kb.add(types.InlineKeyboardButton(L(user_id, "back_main"), callback_data="m:main"))
        bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=kb, disable_web_page_preview=True)
    
    elif action == "news":
        url = channel_link()
        text = f"{L(user_id, 'one_news_intro')}\n\n{one_news_line()}"
        kb = types.InlineKeyboardMarkup()
        if url:
            kb.add(types.InlineKeyboardButton(L(user_id, "go_channel"), url=url))
        kb.add(types.InlineKeyboardButton(L(user_id, "back_main"), callback_data="m:main"))
        bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=kb, disable_web_page_preview=True)
    
    elif action == "catalog":
        text = L(user_id, "catalog_title")
        kb = _catalog_grid_kb(user_id)
        bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=kb)
    
    elif action == "language":
        text = L(user_id, "pick_lang")
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(
            types.InlineKeyboardButton("RU", callback_data="lang:ru"),
            types.InlineKeyboardButton("EN", callback_data="lang:en"),
        )
        kb.add(types.InlineKeyboardButton(L(user_id, "back_main"), callback_data="m:main"))
        bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=kb)
    
    elif action == "about":
        text = L(user_id, "about")
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(L(user_id, "back_main"), callback_data="m:main"))
        bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=kb)
    
    elif action == "tip":
        prices = [
            types.LabeledPrice(MSG["en"]["tip_btn_1"], 500),
            types.LabeledPrice(MSG["en"]["tip_btn_2"], 2000),
            types.LabeledPrice(MSG["en"]["tip_btn_3"], 5000),
        ]
        bot.send_invoice(
            c.message.chat.id,
            title=L(user_id, "tip_title"),
            description=L(user_id, "tip_desc"),
            payload=f"tip-{user_id}-{int(time())}",
            provider_token="",
            currency="XTR",
            prices=prices
        )
    
    elif action == "main":
        text = L(user_id, "welcome")
        kb = build_main_menu(user_id)
        bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=kb)


# =========================
# TIPS
# =========================
@bot.message_handler(commands=['tip'])
def cmd_tip(m):
    prices = [
        types.LabeledPrice(L(m.from_user.id, "tip_btn_1"), 500),   # 5.00 Stars
        types.LabeledPrice(L(m.from_user.id, "tip_btn_2"), 2000),  # 20.00 Stars
        types.LabeledPrice(L(m.from_user.id, "tip_btn_3"), 5000),  # 50.00 Stars
    ]

    bot.send_invoice(
        m.chat.id,
        title=L(m.from_user.id, "tip_title"),
        description=L(m.from_user.id, "tip_desc"),
        payload=f"tip-{m.from_user.id}-{int(datetime.datetime.now().timestamp())}",
        provider_token="",   # пусто = Stars
        currency="XTR",      # именно XTR
        prices=prices
    )
@bot.pre_checkout_query_handler(func=lambda q: True)
def checkout(q):
    bot.answer_pre_checkout_query(q.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(m):
    bot.send_message(m.chat.id, L(m.from_user.id, "thanks_tip"))


# RUN

def main():
    # ... твой код здесь ...

    try:
        schedule_daily()
        scheduler.start()
        logger.info("Scheduler started")
    except Exception as e:
        logger.error(f"Scheduler failed: {e}")
    
    
    try:
        from mobile_fix import setup_mobile_handlers
        setup_mobile_handlers(bot, L, build_main_menu)
        logger.info("Mobile fix activated")
    except ImportError:
        logger.warning("Mobile fix module not found.")
    except Exception as e:
        logger.error(f"Failed to setup mobile fix: {e}")
   
    
    logger.info("Bot polling start")
    bot.infinity_polling(timeout=30, long_polling_timeout=30)

if __name__ == "__main__":
    main()
