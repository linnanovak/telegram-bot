from telebot import types
from src.database.user_data import get_lang
from src.config.texts import MSG

def build_main_menu(user_langs, user_id: int) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=2)
    lang = get_lang(user_langs, user_id)
    
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

def back_to_main_kb(user_langs, user_id: int) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup()
    lang = get_lang(user_langs, user_id)
    text = MSG["ru"]["back_main"] if lang == "ru" else MSG["en"]["back_main"]
    kb.add(types.InlineKeyboardButton(text, callback_data="m:main"))
    return kb
