import json
from pathlib import Path

USER_LANG_FILE = Path("data/user_lang.json")

def load_user_langs():
    try:
        with open(USER_LANG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {int(k): ("ru" if v == "ru" else "en") for k, v in data.items()}
    except FileNotFoundError:
        return {}

def save_user_langs(user_langs):
    USER_LANG_FILE.parent.mkdir(exist_ok=True)
    with open(USER_LANG_FILE, "w", encoding="utf-8") as f:
        json.dump(user_langs, f, ensure_ascii=False, indent=2)

def set_lang(user_langs, user_id: int, lang: str):
    user_langs[user_id] = "ru" if lang == "ru" else "en"
    save_user_langs(user_langs)

def get_lang(user_langs, user_id: int) -> str:
    return user_langs.get(user_id, "en")

def L(user_langs, user_id: int, key: str) -> str:
    from src.config.texts import MSG
    lang = get_lang(user_langs, user_id)
    return MSG["ru" if lang == "ru" else "en"][key]
