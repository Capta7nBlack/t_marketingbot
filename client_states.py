import re

from datetime import datetime
from dateutil.relativedelta import relativedelta

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import text


from timepicker import build_hour_keyboard_clock

from imageloading.imagemaker import overlay_images
from get_absolute_path import absolute_path
from markup_states import markup_default, inline_verification, markup_cancelation

from config import frame_absolute_path, output_absolute_folder, bot_token, under_post_text_switch

from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, DialogCalendar, DialogCalendarCallback, get_user_locale
from aiogram.filters.callback_data import CallbackData

# Initialize bot and dispatcher
bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Define states
class PostStates(StatesGroup):
    uploading_photo = State()
    photo_text = State()
    post_text = State()
    selecting_date = State()
    selecting_time = State()
    final_verification = State()
    payment = State()

# Cancel conversation handler
@dp.message(F.text == "❌ Остановить диалог")
async def cancel_conversation(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Диалог прекращен. Вы можете начать заново", reply_markup=markup_default())

# Start command handler
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(f"Здравствуйте {message.from_user.first_name}, добро пожаловать!", reply_markup=markup_default())

# Create post handler
@dp.message(F.text == "Создать рекламный пост")
async def default_create(message: types.Message, state: FSMContext):
    await state.set_state(PostStates.uploading_photo)
    await message.answer("Отправьте, пожалуйста, фото для поста.", reply_markup=markup_cancelation())

# Show all posts handler
@dp.message(F.text == "Показать все созданные посты")
async def default_showall(message: types.Message):
    await message.answer("This part of the bot is work in progress")

# Handle photo upload
@dp.message(PostStates.uploading_photo, F.photo)
async def handle_photo(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    file_info = await bot.get_file(file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    downloaded_file = downloaded_file.read()
    save_input_path = f"imageloading/user_input_photos/{message.from_user.first_name}_input.jpg"
    with open(save_input_path, "wb") as new_file:
        new_file.write(downloaded_file)

    await message.answer("Фото принято. Теперь отправьте текст для фото.")
    await state.update_data(input_photo_path=absolute_path(save_input_path))
    await state.set_state(PostStates.photo_text)

# Handle invalid photo input
@dp.message(PostStates.uploading_photo)
async def invalid_photo(message: types.Message):
    await message.answer("❌ Отправьте фото, а не текст.", reply_markup=markup_cancelation())

# Handle photo text
@dp.message(PostStates.photo_text, F.text)
async def photo_text(message: types.Message, state: FSMContext):
    safe_text = re.sub(r'[\/:*?"<>|]', '', message.text)
    safe_first_name = re.sub(r'[\/:*?"<>|]', '', message.from_user.first_name)

    data = await state.get_data()
    input_photo_path = data['input_photo_path']

    output_path_file = f"{output_absolute_folder}/{safe_first_name}_{safe_text}_edited.png"
    overlay_images(input_photo_path, frame_absolute_path, output_path_file, message.text)

    await state.update_data(output_photo_path=output_path_file)
    output_photo = FSInputFile(output_path_file)

    
    await message.answer_photo(output_photo)
    await message.answer("Хотите продолжить или попробовать еще раз?", reply_markup=inline_verification("photo_text"))


@dp.message(PostStates.photo_text)
async def invalid_text(message: types.Message, state: FSMContext):
    await message.answer("Вы должны отправить Текст")

# Handle post text
@dp.message(PostStates.post_text)
async def post_text(message: types.Message, state: FSMContext):
    await state.update_data(post_text=message.text)
    
    await message.answer(f'Текст для поста: "{message.text}"\nПродолжим или хотите поменять текст на другой?', reply_markup=inline_verification("post_text"))

# Handle verification callbacks
@dp.callback_query(F.data.startswith(("confirm_", "retry_")))
async def handle_verification(call: types.CallbackQuery, state: FSMContext):
    step = call.data.split("_", 1)[1] if "_" in call.data else call.data

    print(f"Callback data received: {call.data} and step: {step}")  # Log the callback data
    if call.data.startswith("confirm_"):
        if step == "photo_text":
            if under_post_text_switch:
                await state.set_state(PostStates.post_text)
                await call.message.answer("Отправьте текст для поста", reply_markup=markup_cancelation())
            else:
                await state.set_state(PostStates.selecting_date)
                today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
                next_month = datetime.today() + relativedelta(months=1)

                calendar = SimpleCalendar(
                locale='ru-RU', show_alerts=True
                )
                calendar.set_dates_range(today, next_month)
                await call.message.edit_text(
                        f"Выберите дату публикации.",
                           reply_markup=await calendar.start_calendar()
                           )
                await call.answer()
        elif step == "post_text":
            await state.set_state(PostStates.selecting_date)
            today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
            next_month = datetime.today() + relativedelta(months=1)

            calendar = SimpleCalendar(
                locale='ru-RU', show_alerts=True
                )
            calendar.set_dates_range(today, next_month)
            await call.message.edit_text(
                        f"Выберите дату публикации.",
                           reply_markup=await calendar.start_calendar()
                           )
            await call.answer()


        elif step == "selecting_date":
            await state.set_state(PostStates.selecting_time)
            await call.message.edit_text("Теперь выберите время публикации.", reply_markup=build_hour_keyboard_clock())
        elif step == "selecting_time":
            await state.set_state(PostStates.final_verification)
            data = await state.get_data()
            if under_post_text_switch:
                post_text = f"{data['post_text']}\nДата: {data['post_date']}\nВремя: {data['post_time']}"
            else:
                post_text = f"Дата: {data['post_date']}\nВремя: {data['post_time']}"

            with open(data['output_photo_path'], 'rb') as photo:
                await call.message.answer_photo(photo, caption=post_text)

            await call.message.answer("Продолжим или если что-то хотите поменять начните заново", reply_markup=inline_verification("final_verification"))

    elif call.data.startswith("retry_"):
        if step == "photo_text":
            await state.set_state(PostStates.uploading_photo)
            await call.message.answer("Пожалуйста отправьте фото заново", reply_markup=markup_cancelation())
        elif step == "post_text":
            await call.answer()
            await state.set_state(PostStates.post_text)
            await call.message.answer("Пожалуйста отправьте новый текст", reply_markup=markup_cancelation())
        elif step == "selecting_date":

            await state.set_state(PostStates.selecting_date)
            today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
            next_month = datetime.today() + relativedelta(months=1)

            calendar = SimpleCalendar(
                locale='ru-RU', show_alerts=True
                )
            calendar.set_dates_range(today, next_month)
            await call.message.edit_text(
                        f"Выберите дату публикации.",
                           reply_markup=await calendar.start_calendar()
                           )
            await call.answer()

        elif step == "selecting_time":
            await state.set_state(PostStates.selecting_time)
            await call.message.edit_text("Выберите время публикации.", reply_markup=build_hour_keyboard_clock())

    await call.answer()

# Handle calendar callback
@dp.callback_query(SimpleCalendarCallback.filter(), StateFilter(PostStates.selecting_date))
async def selecting_date(callback_query: types.CallbackQuery,callback_data: CallbackData, state: FSMContext):

    calendar = SimpleCalendar(
        locale="ru-RU", show_alerts=True
    )
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    next_month = datetime.today() + relativedelta(months=1)

    calendar.set_dates_range(today, next_month)
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(

            f'You selected {date.strftime("%d/%m/%Y")}\nВы можете поменять дату если ошиблись.',
            reply_markup = inline_verification("selecting_date")
        )
        state.update_data(selecting_date =  date.strftime("%d/%m/%Y"))
# Handle time selection callback
@dp.callback_query(F.data.startswith("hour_") | (F.data == "none"), StateFilter(PostStates.selecting_time))
async def callback_inline(call: types.CallbackQuery, state: FSMContext):
    data = call.data

    if data.startswith("hour_"):
        chosen_hour = data.split("_")[1]
        await state.update_data(selected_time = chosen_hour)
        # ✅ Edit message text to show the selected hour
        await call.message.edit_text(f"Hour chosen: {chosen_hour}")

    await call.answer()  # ✅ Always close the callback query to avoid "loading" state

# Start polling
if __name__ == '__main__':
    dp.run_polling(bot)
