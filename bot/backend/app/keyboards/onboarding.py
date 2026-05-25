from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.texts import ru

CONSENT_AGREE_CB = "consent:agree"
CONSENT_DECLINE_CB = "consent:decline"


def consent_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=ru.CONSENT_BUTTON_AGREE,
                    callback_data=CONSENT_AGREE_CB,
                ),
                InlineKeyboardButton(
                    text=ru.CONSENT_BUTTON_DECLINE,
                    callback_data=CONSENT_DECLINE_CB,
                ),
            ]
        ]
    )


def email_skip_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=ru.EMAIL_SKIP_BUTTON)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def open_webapp_keyboard() -> InlineKeyboardMarkup:
    """Заглушка кнопки перехода в веб-приложение.

    Реальный URL/WebApp подключим, когда мини-апп будет готов.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=ru.OPEN_WEBAPP_BUTTON,
                    url=ru.WEBAPP_PLACEHOLDER_URL,
                )
            ]
        ]
    )
