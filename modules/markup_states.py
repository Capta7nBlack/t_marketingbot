from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def markup_default():
    """Creates the default reply keyboard with main options."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Создать рекламный пост"), KeyboardButton(text="Показать все созданные посты")]
        ],
        resize_keyboard=True
    )


def inline_verification(step: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data=f"confirm_{step}")
    builder.button(text="🔄 Повторить", callback_data=f"retry_{step}")
    return builder.as_markup()


def markup_cancelation():
    """Creates a reply keyboard with a cancel button."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Остановить диалог")]
        ],
        resize_keyboard=True
    )
