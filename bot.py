import telebot
from src.config.settings import BOT_TOKEN, OWNER_USERNAME
from src.database.user_data import load_user_langs
from src.utils.logger import setup_logging, setup_user_logger
from src.handlers.start import setup_start_handlers
from src.handlers.menu import setup_menu_handlers
from src.handlers.catalog import setup_catalog_handlers
from src.handlers.tips import setup_tips_handlers
from src.services.muskfeed import setup_scheduler
from mobile_fix import setup_mobile_handlers

# Инициализация
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
logger = setup_logging()
user_logger = setup_user_logger()
user_langs = load_user_langs()

# Настройка обработчиков
setup_start_handlers(bot, user_langs, logger, user_logger)
setup_menu_handlers(bot, user_langs, logger)
setup_catalog_handlers(bot, user_langs, logger)
setup_tips_handlers(bot, user_langs, logger)

# Мобильные фиксы
try:
    from mobile_fix import setup_mobile_handlers
    setup_mobile_handlers(bot, lambda user_id, key: L(user_langs, user_id, key), lambda user_id: build_main_menu(user_langs, user_id))
    logger.info("Mobile fix activated")
except ImportError:
    logger.warning("Mobile fix module not found.")
except Exception as e:
    logger.error(f"Failed to setup mobile fix: {e}")

# Планировщик
setup_scheduler(bot, logger)

# Вспомогательные функции (для mobile_fix)
def L(user_langs, user_id: int, key: str) -> str:
    from src.database.user_data import get_lang
    from src.config.texts import MSG
    lang = get_lang(user_langs, user_id)
    return MSG["ru" if lang == "ru" else "en"][key]

def build_main_menu(user_langs, user_id: int):
    from src.keyboards.main_menu import build_main_menu as build_menu
    return build_menu(user_langs, user_id)

# Запуск
if __name__ == "__main__":
    logger.info("Bot starting with new modular structure...")
    bot.infinity_polling(timeout=30, long_polling_timeout=30)
