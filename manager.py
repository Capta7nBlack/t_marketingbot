from config import manager_bot_token, allowed_users

from datetime import datetime
from dateutil.relativedelta import relativedelta

from modules import db
from modules.markup_states import markup_manager_default
from modules.datepicker import months_ru

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import text
from aiogram.filters.callback_data import CallbackData

from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, get_user_locale



bot = Bot(token=manager_bot_token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)



class Manager(StatesGroup):
    authorized = State()
    min_date = State()
    max_date = State()
    specific_date = State()


@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    username = message.from_user.username  # Get the sender's username
    print(username)
    
    if username in allowed_users or "@" + username in allowed_users or username[1:] in allowed_users:
        await state.set_state(Manager.authorized)
        await message.reply(f"Welcome, {username}! You are authorized. ✅",
                            reply_markup = markup_manager_default()
                            )
    else:
        await message.reply("❌ You are not authorized to use this bot.")


@dp.message(StateFilter(Manager.authorized), F.text == "Показать посты за промежуток времени")
async def show_between(message: types.Message, state: FSMContext):
        await state.set_state(Manager.min_date)

        calendar = SimpleCalendar(
                locale='ru-RU', show_alerts=True
                )
        await message.answer(
                        f"Выберите стартовую и конечную дату диапозона для постов.",
                           reply_markup=await calendar.start_calendar()
                           )
 
@dp.message(StateFilter(Manager.authorized), F.text == "Показать посты на сегодня")
async def show_today(message: types.Message, state: FSMContext):
        await state.set_state(Manager.authorized)
        
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        today_str = today.strftime("%Y-%m-%d")

        data = db.show_between(today_str,today_str)
        i = 1
        if data:
                for photo_path, post_text, post_date, post_time, kaspi_path in data:
                    
                    
                    date_obj = datetime.strptime(post_date, "%Y-%m-%d")           
                    formatted_date = f"{date_obj.year}, {date_obj.day} {months_ru[date_obj.month]}"
                        
                    if post_text: 
                        post_text = f"Текст под постом: '{post_text}'\nДата: {formatted_date}\nВремя: {post_time}"
                    else:
                        post_text = f"Дата: {formatted_date}\nВремя: {post_time}"
                    distance = "\n---\n---\n---"

                    output_photo = FSInputFile(photo_path)
                    pdf_file = FSInputFile(kaspi_path)
                    await message.answer(f"Пост номер: {i}", 
                                                        reply_markup=markup_manager_default()
                                                        )
                    i = i + 1 # ЗНАЮ ЧТО ЭТО СМЕШНО, НО МНЕ НЕ НРАВИТЬСЯ enumerate
                    await message.answer_document(output_photo,caption = post_text)
                    await message.answer_document(pdf_file, caption=distance)

        else:
            await message.answer(f"На сегодня нет рекламных постов",
                                                reply_markup=markup_manager_default()
                                                )

        await state.set_state(Manager.authorized)

                    
@dp.message(StateFilter(Manager.authorized), F.text == "Показать посты за конкретную дату")
async def show_specific(message: types.Message, state: FSMContext):
    await state.set_state(Manager.specific_date)

    calendar = SimpleCalendar(
                locale='ru-RU', show_alerts=True
                )
    await message.answer(
                        f"Выберите дату в которой хотите видеть список постов.",
                           reply_markup=await calendar.start_calendar()
                           )
                  



@dp.callback_query(SimpleCalendarCallback.filter(), StateFilter(Manager.min_date))
async def selecting_min(callback_query: types.CallbackQuery,callback_data: CallbackData, state: FSMContext):

    calendar = SimpleCalendar(
        locale="ru-RU", show_alerts=True
    )

    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        
        calendar_max = SimpleCalendar(
                locale='ru-RU', show_alerts=True
                )

        min_date = date.strftime("%Y-%m-%d")
        mindate_object = datetime.strptime(min_date, "%Y-%m-%d")
        next_year = mindate_object + relativedelta(years=1)

        calendar_max.set_dates_range(mindate_object, next_year)

        await state.update_data(min_date=min_date)
        await state.set_state(Manager.max_date)

        formatted_date = f"{date.year}, {date.day} {months_ru[date.month]}"

        await callback_query.message.answer(

            f'Вы выбрали {formatted_date} как стартовую дату.\nТеперь выберите конечную дату.',
            reply_markup = await calendar_max.start_calendar()
            )

@dp.callback_query(SimpleCalendarCallback.filter(), StateFilter(Manager.max_date))
async def selecting_max(callback_query: types.CallbackQuery,callback_data: CallbackData, state: FSMContext):
    calendar = SimpleCalendar(
        locale="ru-RU", show_alerts=True
    )

    selected, date = await calendar.process_selection(callback_query, callback_data)


    if selected:

        formatted_date = f"{date.year}, {date.day} {months_ru[date.month]}"
        await callback_query.message.answer(
            f'Вы выбрали {formatted_date} как конечную дату.',
            reply_markup = markup_manager_default()
            )
    
        data_date = await state.get_data() 
        min_date = data_date.get('min_date')
        max_date = date.strftime("%Y-%m-%d")
        data = db.show_between(min_date,max_date)
        i = 1
        if data:
                for photo_path, post_text, post_date, post_time, kaspi_path in data:
                    
                    
                    date_obj = datetime.strptime(post_date, "%Y-%m-%d")           
                    formatted_date = f"{date_obj.year}, {date_obj.day} {months_ru[date_obj.month]}"
                        
                    if post_text: 
                        post_text = f"Текст под постом: '{post_text}'\nДата: {formatted_date}\nВремя: {post_time}"
                    else:
                        post_text = f"Дата: {formatted_date}\nВремя: {post_time}"
                    distance = "\n---\n---\n---"

                    output_photo = FSInputFile(photo_path)
                    pdf_file = FSInputFile(kaspi_path)
                    await callback_query.message.answer(f"Пост номер: {i}")
                    i = i + 1 # ЗНАЮ ЧТО ЭТО СМЕШНО, НО МНЕ НЕ НРАВИТЬСЯ enumerate
                    await callback_query.message.answer_document(output_photo,caption = post_text)
                    await callback_query.message.answer_document(pdf_file, caption=distance)
                    await state.set_state(Manager.authorized)
        else:
            await callback_query.message.answer(f"В этом промежутке времене не было зарегистрировано рекламных постов.")
            await state.set_state(Manager.authorized)
        await callback_query.answer()

        

@dp.callback_query(SimpleCalendarCallback.filter(), StateFilter(Manager.specific_date))
async def selecting_specific(callback_query: types.CallbackQuery,callback_data: CallbackData, state: FSMContext):

    calendar = SimpleCalendar(
        locale="ru-RU", show_alerts=True
    )

    selected, date = await calendar.process_selection(callback_query, callback_data)


    specific_date = ""

    if selected:

        specific_date = date.strftime("%Y-%m-%d")
        await state.set_state(Manager.authorized)
        formatted_date = f"{date.year}, {date.day} {months_ru[date.month]}"
        await callback_query.message.answer(
            f'Вы выбрали {formatted_date}.',
            reply_markup = markup_manager_default()
            )

         
        data = db.show_between(specific_date,specific_date)
        i = 1
        if data:
                for photo_path, post_text, post_date, post_time, kaspi_path in data:
                    
                    
                    date_obj = datetime.strptime(post_date, "%Y-%m-%d")           
                    formatted_date = f"{date_obj.year}, {date_obj.day} {months_ru[date_obj.month]}"
                        
                    if post_text: 
                        post_text = f"Текст под постом: '{post_text}'\nДата: {formatted_date}\nВремя: {post_time}"
                    else:
                        post_text = f"Дата: {formatted_date}\nВремя: {post_time}"
                    distance = "\n---\n---\n---"

                    output_photo = FSInputFile(photo_path)
                    pdf_file = FSInputFile(kaspi_path)
                    await callback_query.message.answer(f"Пост номер: {i}",
                                                        reply_markup = markup_manager_default()
                                                        )
                    i = i + 1 # ЗНАЮ ЧТО ЭТО СМЕШНО, НО МНЕ НЕ НРАВИТЬСЯ enumerate
                    await callback_query.message.answer_document(output_photo,caption = post_text)
                    await callback_query.message.answer_document(pdf_file, caption=distance)
                    await state.set_state(Manager.authorized)
        else:
            await callback_query.message.answer(f"В этой дате не было зарегистрировано рекламных постов.")
            await state.set_state(Manager.authorized)

        await callback_query.answer()






if __name__ == '__main__':
    dp.run_polling(bot)
