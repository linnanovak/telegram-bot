from telebot import types
from src.database.analytics import track_event
from src.keyboards.main_menu import build_main_menu, back_to_main_kb
from src.keyboards.catalog_kb import build_catalog_keyboard, _catalog_grid_kb
from src.services.muskfeed import one_news_line
from src.config.settings import OWNER_USERNAME
from src.config.texts import MSG

def L(user_langs, user_id: int, key: str) -> str:
    from src.database.user_data import get_lang
    lang = get_lang(user_langs, user_id)
    return MSG["ru" if lang == "ru" else "en"][key]

def channel_link(bot):
    from src.config.settings import NEWS_CHANNEL_USERNAME, NEWS_CHAT_ID
    if NEWS_CHANNEL_USERNAME:
        return f"https://t.me/{NEWS_CHANNEL_USERNAME}"
    if NEWS_CHAT_ID:
        try:
            link = bot.create_chat_invite_link(int(NEWS_CHAT_ID), name="bot-channel-link")
            return link.invite_link
        except Exception:
            return ""
    return ""

def setup_menu_handlers(bot, user_langs, logger):
    
    @bot.message_handler(commands=["status"])
    def cmd_status(m):
        track_event(m.from_user, "cmd_status")
        bot.send_message(m.chat.id, L(user_langs, m.from_user.id, "status"))

    @bot.message_handler(commands=["channel"])
    def cmd_channel(m):
        url = channel_link(bot)
        if url:
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton(L(user_langs, m.from_user.id, "channel_here"), url=url))
            bot.send_message(m.chat.id, L(user_langs, m.from_user.id, "channel_here"), reply_markup=kb, disable_web_page_preview=True)
        else:
            bot.send_message(m.chat.id, "Channel link is not configured.")

    @bot.message_handler(commands=["news_now"])
    def cmd_news_now(m):
        url = channel_link(bot)
        text = f"{L(user_langs, m.from_user.id, 'one_news_intro')}\\n\\n{one_news_line()}"
        if url:
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton(L(user_langs, m.from_user.id, "go_channel"), url=url))
            bot.send_message(m.chat.id, text, reply_markup=kb, disable_web_page_preview=True)
        else:
            bot.send_message(m.chat.id, text)

    @bot.message_handler(commands=["menu"])
    def cmd_menu(m):
        bot.send_message(m.chat.id, L(user_langs, m.from_user.id, "welcome"), reply_markup=build_main_menu(user_langs, m.from_user.id))

    @bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("m:"))
    def on_menu_click(c: types.CallbackQuery):
        user_id = c.from_user.id
        action = c.data.split(":", 1)[1]

        # analytics
        track_event(c.from_user, "menu_click", {"action": action})

        bot.answer_callback_query(c.id)

        if action == "status":
            text = L(user_langs, user_id, "status")
            kb = back_to_main_kb(user_langs, user_id)
            bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=kb)

        elif action == "channel":
            url = channel_link(bot)
            text = L(user_langs, user_id, "channel_here")
            kb = types.InlineKeyboardMarkup()
            if url:
                kb.add(types.InlineKeyboardButton(L(user_langs, user_id, "go_channel"), url=url))
            kb.add(types.InlineKeyboardButton(L(user_langs, user_id, "back_main"), callback_data="m:main"))
            bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=kb, disable_web_page_preview=True)

        elif action == "news":
            url = channel_link(bot)
            text = f"{L(user_langs, user_id, 'one_news_intro')}\\n\\n{one_news_line()}"
            kb = types.InlineKeyboardMarkup()
            if url:
                kb.add(types.InlineKeyboardButton(L(user_langs, user_id, "go_channel"), url=url))
            kb.add(types.InlineKeyboardButton(L(user_langs, user_id, "back_main"), callback_data="m:main"))
            bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=kb, disable_web_page_preview=True)
        
        elif action == "catalog":
            text = L(user_langs, user_id, "catalog_title")
            kb = build_catalog_keyboard(user_langs, user_id)
            bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=kb)
        
        elif action == "language":
            text = L(user_langs, user_id, "pick_lang")
            kb = types.InlineKeyboardMarkup(row_width=2)
            kb.add(
                types.InlineKeyboardButton("RU", callback_data="lang:ru"),
                types.InlineKeyboardButton("EN", callback_data="lang:en"),
            )
            kb.add(types.InlineKeyboardButton(L(user_langs, user_id, "back_main"), callback_data="m:main"))
            bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=kb)
        
        elif action == "about":
            text = L(user_langs, user_id, "about")
            kb = back_to_main_kb(user_langs, user_id)
            bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=kb)
        
        elif action == "main":
            text = L(user_langs, user_id, "welcome")
            kb = build_main_menu(user_langs, user_id)
            bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=kb)

    logger.info("Menu handlers installed")
