
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
from config import user_bot_token

TOKEN = user_bot_token
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Generate an inline calendar for the next 14 days

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

calendar_days = 12
items_per_column = 3




def create_calendar():


    months_ru_abb = {
        "Jan": "Янв", "Feb": "Фев", "Mar": "Мар", "Apr": "Апр",
        "May": "Май", "Jun": "Июн", "Jul": "Июл", "Aug": "Авг",
        "Sep": "Сен", "Oct": "Окт", "Nov": "Ноя", "Dec": "Дек"
    }
    


    builder = InlineKeyboardBuilder()

    today = datetime.today()
    current_time = datetime.now().hour  

    for i in range(calendar_days):
        date = today + timedelta(days=i)
        if current_time > 21 and i == 0: # handling the case when there is no time for today's date
            continue
        builder.button(
            text=(today + timedelta(days=i)).strftime("%d %b").replace(
                (today + timedelta(days=i)).strftime("%b"),
                months_ru_abb[(today + timedelta(days=i)).strftime("%b")]
                ),
            callback_data=date.strftime("date_%Y-%m-%d")
        )

        # handling the case when there is no time for today's date
    if current_time > 21:
        date = today + timedelta(days=calendar_days)

        builder.button(
            text=(today + timedelta(days=calendar_days)).strftime("%d %b").replace(
                (today + timedelta(days=calendar_days)).strftime("%b"),
                months_ru_abb[(today + timedelta(days=calendar_days)).strftime("%b")]
                ),
            callback_data=date.strftime("date_%Y-%m-%d")
        )

    builder.adjust(items_per_column)
    return builder.as_markup()

@dp.message(F.text.lower() == "pick date")
async def send_calendar(message: Message):
    await message.answer(
            "Пожалуйста выберите время публикации:",
        reply_markup=create_calendar()
    )

months_ru = {
    1: "Января", 2: "Февраля", 3: "Марта", 4: "Апреля",
    5: "Мая", 6: "Июня", 7: "Июля", 8: "Августа",
    9: "Сентября", 10: "Октября", 11: "Ноября", 12: "Декабря"
}

@dp.callback_query(F.data.startswith("date_"))
async def handle_date_pick(callback: CallbackQuery):
    selected_date = callback.data.replace("date_", "")
    
    date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
    formatted_date = f"{date_obj.year}, {date_obj.day} {months_ru[date_obj.month]}"
    # state.update_data(selected_date=selected_date)
    await callback.message.answer(f"Вы выбрали {formatted_date}")
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
