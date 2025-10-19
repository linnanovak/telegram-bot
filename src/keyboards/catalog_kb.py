from telebot import types
from src.database.user_data import get_lang
from src.config.texts import MSG

PACKAGE_ORDER = ["simple", "simple_custom", "integrations", "ai_ultra"]

def L(user_langs, user_id: int, key: str) -> str:
    lang = get_lang(user_langs, user_id)
    return MSG["ru" if lang == "ru" else "en"][key]

def build_catalog_keyboard(user_langs, user_id: int) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton(L(user_langs, user_id, "back_main"), callback_data="m:main"))
    kb.add(
        types.InlineKeyboardButton(L(user_langs, user_id, "catalog_btn_simple"), callback_data="pkg:simple"),
        types.InlineKeyboardButton(L(user_langs, user_id, "catalog_btn_simple_custom"), callback_data="pkg:simple_custom"),
        types.InlineKeyboardButton(L(user_langs, user_id, "catalog_btn_integrations"), callback_data="pkg:integrations"),
        types.InlineKeyboardButton(L(user_langs, user_id, "catalog_btn_ai_ultra"), callback_data="pkg:ai_ultra"),
    )
    kb.add(types.InlineKeyboardButton(L(user_langs, user_id, "catalog_btn_sale"), callback_data="promo:sale"))
    kb.add(types.InlineKeyboardButton(L(user_langs, user_id, "catalog_btn_contact"), url=f"https://t.me/YOUR_USERNAME"))
    return kb

def _catalog_detail_kb(user_langs, user_id: int, current_key: str) -> types.InlineKeyboardMarkup:
    i = PACKAGE_ORDER.index(current_key)
    prev_key = PACKAGE_ORDER[(i - 1) % len(PACKAGE_ORDER)]
    next_key = PACKAGE_ORDER[(i + 1) % len(PACKAGE_ORDER)]

    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton(L(user_langs, user_id, "prev"), callback_data=f"pkg:{prev_key}"),
        types.InlineKeyboardButton(L(user_langs, user_id, "back_catalog"), callback_data="nav:back"),
        types.InlineKeyboardButton(L(user_langs, user_id, "next"), callback_data=f"pkg:{next_key}"),
    )
    kb.add(types.InlineKeyboardButton(L(user_langs, user_id, "back_main"), callback_data="m:main"))
    kb.add(types.InlineKeyboardButton(L(user_langs, user_id, "catalog_btn_contact"), url=f"https://t.me/YOUR_USERNAME"))
    return kb

def _catalog_detail_text(user_langs, user_id: int, key: str) -> str:
    lang = "ru" if get_lang(user_langs, user_id) == "ru" else "en"
    mapping = {
        "simple": MSG[lang]["card_simple"],
        "simple_custom": MSG[lang]["card_simple_custom"],
        "integrations": MSG[lang]["card_integrations"],
        "ai_ultra": MSG[lang]["card_ai_ultra"],
    }
    return mapping.get(key, "…")

def _catalog_grid_kb(user_langs, user_id: int):
    return build_catalog_keyboard(user_langs, user_id)
