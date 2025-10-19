from telebot import types
from telebot.types import BotCommand, BotCommandScopeChat
from src.database.user_data import set_lang, get_lang
from src.database.analytics import track_event
from src.keyboards.main_menu import build_main_menu
from src.config.texts import MSG

def apply_commands(bot, chat_id: int, lang: str):
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

def L(user_langs, user_id: int, key: str) -> str:
    lang = get_lang(user_langs, user_id)
    return MSG["ru" if lang == "ru" else "en"][key]

def setup_start_handlers(bot, user_langs, logger, user_logger):
    
    def log_user_info(m):
        txt = f"ID:{m.from_user.id} | name:{m.from_user.first_name} | text:{(m.text or '').strip()}"
        user_logger.info(txt)

    @bot.message_handler(commands=["start"])
    def cmd_start(m):
        log_user_info(m)
        # analytics: кто зашёл и откуда (deep-link payload)
        payload = ""
        if m.text and " " in m.text:
            payload = m.text.split(" ", 1)[1].strip()
        track_event(m.from_user, "cmd_start", {"payload": payload})

        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(
            types.InlineKeyboardButton("RU", callback_data="lang:ru"),
            types.InlineKeyboardButton("EN", callback_data="lang:en"),
        )
        bot.send_message(m.chat.id, L(user_langs, m.from_user.id, "start"), reply_markup=kb)
    
    @bot.message_handler(commands=["language"])
    def cmd_language(m):
        log_user_info(m)
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(
            types.InlineKeyboardButton("RU", callback_data="lang:ru"),
            types.InlineKeyboardButton("EN", callback_data="lang:en"),
        )
        bot.send_message(m.chat.id, L(user_langs, m.from_user.id, "pick_lang"), reply_markup=kb)

    @bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("lang:"))
    def on_lang(c: types.CallbackQuery):
        bot.answer_callback_query(c.id)
        lang = c.data.split(":", 1)[1]

        # analytics
        track_event(c.from_user, "lang_set", {"lang": lang})

        set_lang(user_langs, c.from_user.id, lang)
        apply_commands(bot, c.message.chat.id, lang)
        
        text = L(user_langs, c.from_user.id, "welcome")
        kb = build_main_menu(user_langs, c.from_user.id)
        
        try:
            bot.edit_message_text(
                text,
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                reply_markup=kb
            )
        except Exception:
            bot.send_message(c.message.chat.id, text, reply_markup=kb)

    logger.info("Start handlers installed")
