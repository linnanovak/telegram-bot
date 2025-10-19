import datetime
from telebot import types
from src.database.analytics import track_event
from src.config.texts import MSG

def L(user_langs, user_id: int, key: str) -> str:
    from src.database.user_data import get_lang
    lang = get_lang(user_langs, user_id)
    return MSG["ru" if lang == "ru" else "en"][key]

def setup_tips_handlers(bot, user_langs, logger):

    @bot.callback_query_handler(func=lambda c: c.data == "m:tip")
    def on_tip_click(c: types.CallbackQuery):
        user_id = c.from_user.id
        prices = [
            types.LabeledPrice(MSG["en"]["tip_btn_1"], 500),
            types.LabeledPrice(MSG["en"]["tip_btn_2"], 2000),
            types.LabeledPrice(MSG["en"]["tip_btn_3"], 5000),
        ]
        bot.send_invoice(
            c.message.chat.id,
            title=L(user_langs, user_id, "tip_title"),
            description=L(user_langs, user_id, "tip_desc"),
            payload=f"tip-{user_id}-{int(datetime.datetime.now().timestamp())}",
            provider_token="",
            currency="XTR",
            prices=prices
        )

    @bot.message_handler(commands=['tip'])
    def cmd_tip(m):
        track_event(m.from_user, "tip_open")
        prices = [
            types.LabeledPrice(L(user_langs, m.from_user.id, "tip_btn_1"), 500),   # 5.00 Stars
            types.LabeledPrice(L(user_langs, m.from_user.id, "tip_btn_2"), 2000),  # 20.00 Stars
            types.LabeledPrice(L(user_langs, m.from_user.id, "tip_btn_3"), 5000),  # 50.00 Stars
        ]

        bot.send_invoice(
            m.chat.id,
            title=L(user_langs, m.from_user.id, "tip_title"),
            description=L(user_langs, m.from_user.id, "tip_desc"),
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
        sp = m.successful_payment
        # analytics
        track_event(m.from_user, "tip_paid", {"amount": sp.total_amount, "currency": sp.currency})

        bot.send_message(m.chat.id, L(user_langs, m.from_user.id, "thanks_tip"))

    logger.info("Tips handlers installed")
