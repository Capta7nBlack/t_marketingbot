import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import F
from aiogram.filters import StateFilter


# ✅ Function to Build Hour Keyboard in a Clock Layout
def build_hour_keyboard_clock() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(inline_keyboard=[])

    # This 2D list represents the 'shape' of the clock
    clock_layout = [
        [0,  0,  0, 12, 0,  0,  0],
        [0,  0, 11,  0, 13,  0,  0],
        [0, 10,  0,  0, 0,  14,  0],
        [9,  0,  0,  0, 0,  0,  15],
        [0,  8,  0,  0, 0,  16,  0],
        [0,  0,  7,  0, 17,  0,  0],
        [0,  0,  0,  18, 0,  0,  0]
    ]

    for row in clock_layout:
        buttons = []
        for cell in row:
            if cell == 0:
                # Blank button to maintain layout (callback_data="none" to avoid errors)
                buttons.append(InlineKeyboardButton(text = " ", callback_data="none"))
            else:
                # Hour button with formatted text
                hour_text = f"{cell}:00"
                buttons.append(InlineKeyboardButton(text = hour_text, callback_data=f"hour_{hour_text}"))
        
        # Add row to inline keyboard
        markup.inline_keyboard.append(buttons)

    return markup


# ✅ Handling the Button Clicks in aiogram v3
# @dp.callback_query(F.data.startswith("hour_") | (F.data == "none"))
async def callback_inline(call: CallbackQuery):
    data = call.data

    if data.startswith("hour_"):
        chosen_hour = data.split("_")[1]

        # ✅ Edit message text to show the selected hour
        await call.message.edit_text(f"Hour chosen: {chosen_hour}")

    await call.answer()  # ✅ Always close the callback query to avoid "loading" state

