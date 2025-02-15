from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from modules.text import text_buttons

def markup_default():
    """Creates the default reply keyboard with main options."""

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=text_buttons.get('default_create')), KeyboardButton(text=text_buttons.get('default_showall'))]
        ],
        resize_keyboard=True
    )
def markup_manager_default():
    """Creates the default reply keyboard with main options."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Показать посты на сегодня")],
            [KeyboardButton(text="Показать посты за промежуток времени"), KeyboardButton(text="Показать посты за конкретную дату")]
        ],
        resize_keyboard=True
    )


def inline_verification(step: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=text_buttons.get('verification_confirm'), callback_data=f"confirm_{step}")
    builder.button(text=text_buttons.get('verification_retry'), callback_data=f"retry_{step}")
    return builder.as_markup()


def markup_cancelation():
    """Creates a reply keyboard with a cancel button."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=text_buttons.get('cancelation'))]
        ],
        resize_keyboard=True
    )






