import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import F
from aiogram.filters import StateFilter

import datetime


# ✅ Function to Build Hour Keyboard in a Clock Layout
def build_hour_keyboard_clock() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(inline_keyboard=[])

    # Get the current hour
    add_hours = 1 # because if it is 15:24, it should start from 16:00. Not from 15:00
    current_hour = (datetime.datetime.now() + datetime.timedelta(hours=add_hours)).hour

    # Clock layout from 9:00 to 23:00
    clock_layout = list(range(9, 24))

    for hour in clock_layout:
        if hour >= current_hour:
            hour_text = f"{hour}:00"
            button = InlineKeyboardButton(
                text=hour_text,
                callback_data=f"hour_{hour_text}"
            )
            markup.inline_keyboard.append([button])

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

