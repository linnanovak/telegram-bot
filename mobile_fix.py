import logging
from telebot import types

logger = logging.getLogger("ash")

def setup_mobile_handlers(bot, L, build_main_menu):
    """
    Устанавливает обработчики для исправления проблем на мобильных устройствах.
    :param bot: объект TeleBot.
    :param L: функция-переводчик.
    :param build_main_menu: функция для создания главного меню.
    """
    
    # AB
    @bot.message_handler(commands=['меню', 'menu', 'startmobile'])
    def mobile_menu_command(m):
        try:
            kb = build_main_menu(m.from_user.id)
            bot.send_message(m.chat.id, L(m.from_user.id, "welcome"), reply_markup=kb)
        except Exception as e:
            logger.error(f"Mobile menu error: {e}")
            bot.send_message(m.chat.id, "Кнопки меню временно недоступны. Попробуйте ввести /start или /language.")

    # lite AB
    @bot.callback_query_handler(func=lambda c: c.data in ['m:main', 'mobile:main'])
    def mobile_simple_callbacks(c):
        try:
            bot.answer_callback_query(c.id)
            kb = build_main_menu(c.from_user.id)
            bot.edit_message_text(
                L(c.from_user.id, "welcome"),
                c.message.chat.id,
                c.message.message_id,
                reply_markup=kb
            )
        except Exception as e:
            logger.error(f"Mobile callback error: {e}")
            bot.answer_callback_query(c.id, "Не удалось обновить меню. Попробуйте снова.")

    logger.info("Mobile fix handlers installed")
