from telebot import types
from src.database.analytics import track_event
from src.database.user_data import set_lang, get_lang
from src.keyboards.catalog_kb import build_catalog_keyboard, _catalog_detail_kb, _catalog_detail_text, PACKAGE_ORDER
from src.config.texts import MSG

def L(user_langs, user_id: int, key: str) -> str:
    lang = get_lang(user_langs, user_id)
    return MSG["ru" if lang == "ru" else "en"][key]

def setup_catalog_handlers(bot, user_langs, logger):

    @bot.message_handler(commands=["catalog"])
    def cmd_catalog(m):
        track_event(m.from_user, "cmd_catalog")
        if get_lang(user_langs, m.from_user.id) not in ("ru", "en"):
            set_lang(user_langs, m.from_user.id, "en")
        bot.send_message(m.chat.id, L(user_langs, m.from_user.id, "catalog_title"), reply_markup=build_catalog_keyboard(user_langs, m.from_user.id))

    @bot.callback_query_handler(func=lambda c: c.data and c.data.startswith(("pkg:", "promo:", "nav:")))
    def on_catalog_click(c: types.CallbackQuery):
        uid = c.from_user.id
        data = c.data

        try:
            if data.startswith("pkg:"):
                key = data.split(":", 1)[1]
                # analytics
                track_event(c.from_user, "catalog_pkg", {"key": key})
                text = _catalog_detail_text(user_langs, uid, key)
                kb = _catalog_detail_kb(user_langs, uid, key)
                bot.edit_message_text(
                    text,
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    reply_markup=kb,
                    disable_web_page_preview=True
                )

            elif data == "nav:back":
                # analytics
                track_event(c.from_user, "catalog_back")
                bot.edit_message_text(
                    L(user_langs, uid, "catalog_title"),
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    reply_markup=build_catalog_keyboard(user_langs, uid)
                )

            elif data == "promo:sale":
                # analytics
                track_event(c.from_user, "promo_open")
                txt = MSG["ru"]["sale"] if get_lang(user_langs, uid) == "ru" else MSG["en"]["sale"]
                kb = types.InlineKeyboardMarkup()
                kb.add(types.InlineKeyboardButton(L(user_langs, uid, "back_catalog"), callback_data="nav:back"))
                kb.add(types.InlineKeyboardButton(L(user_langs, uid, "back_main"), callback_data="m:main"))
                kb.add(types.InlineKeyboardButton(L(user_langs, uid, "catalog_btn_contact"), url=f"https://t.me/limmzxs"))
                bot.edit_message_text(
                    txt,
                    chat_id=c.message.chat.id,
                    message_id=c.message.message_id,
                    reply_markup=kb,
                    disable_web_page_preview=True
                )
        except Exception as e:
            logger.error(f"Catalog error: {e}")
            try:
                bot.answer_callback_query(c.id, "Error, try again")
            except Exception:
                pass

    logger.info("Catalog handlers installed")
