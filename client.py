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

from modules.hash import hashed
from modules.timepicker import build_hour_keyboard_clock
from modules import db
from modules.markup_states import markup_default, inline_verification, markup_cancelation
from modules.get_absolute_path import absolute_path
from modules.datepicker import create_calendar
from modules.datepicker import months_ru


from imageloading.imagemaker import overlay_images

from config import frame_absolute_path, output_absolute_folder, user_bot_token, under_post_text_switch 
from config import input_absolute_folder, receipts_absolute_folder, admin_telegram



# Initialize bot and dispatcher
bot = Bot(token=user_bot_token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

try:
   db.create()
   db.delete_actual_files(db.fetch_and_clean_old_records())
except Exception as e:
    print("Случился казус:", e)


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
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(f"Здравствуйте {message.from_user.first_name}, добро пожаловать!", reply_markup=markup_default())

# Create post handler
@dp.message(F.text == "Создать рекламный пост")
async def default_create(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(PostStates.uploading_photo)
    await message.answer("Отправьте, пожалуйста, фото для поста.", reply_markup=markup_cancelation())

# Show all posts handler
@dp.message(F.text == "Показать все созданные посты")
async def default_showall(message: types.Message, state: FSMContext):

    await state.clear()

    data = db.show_all(message.chat.id)
    i = 1
    if data:
        for photo_path, post_text, post_date, post_time, kaspi_path in data:
            print(post_date)
            date_obj = datetime.strptime(post_date, "%Y-%m-%d")           
            formatted_date = f"{date_obj.year}, {date_obj.day} {months_ru[date_obj.month]}"
            print("photo_path:",photo_path)    
            print("kaspi_path:",kaspi_path)
            if post_text: 
                post_text = f"Текст под постом: '{post_text}'\nДата: {formatted_date}\nВремя: {post_time}"
            else:
                post_text = f"Дата: {formatted_date}\nВремя: {post_time}"
            distance = "\n---\n---\n---"

            output_photo = FSInputFile(photo_path)
            pdf_file = FSInputFile(kaspi_path)
            await message.answer(f"Пост номер: {i}")
            i = i + 1 # ЗНАЮ ЧТО ЭТО СМЕШНО, НО МНЕ НЕ НРАВИТЬСЯ enumerate
            await message.answer_document(output_photo,caption = post_text)
            await message.answer_document(pdf_file, caption=distance)
        await message.answer(f"Если вы хотите отменить рекламный пост и сделать возврат средств, то обратитесь к менеджеру - {admin_telegram}")

    else:
        await message.answer(f"Вы еще не создали ни одного поста для рекламы. Для этого чтобы это сделать нажмите кнопку 'Создать рекламный пост'", reply_markup = markup_default()
                             )


# Handle photo upload
@dp.message(StateFilter(PostStates.uploading_photo), F.photo)
async def handle_photo(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    file_info = await bot.get_file(file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    downloaded_file = downloaded_file.read()
    save_input_path = f"{input_absolute_folder}{message.from_user.first_name}_input.jpg"
    with open(save_input_path, "wb") as new_file:
        new_file.write(downloaded_file)

    await message.answer("Фото принято. Теперь отправьте текст для фото.")
    await state.update_data(input_photo_path=absolute_path(save_input_path))
    await state.set_state(PostStates.photo_text)


@dp.message(StateFilter(PostStates.uploading_photo), F.document, F.document.mime_type.startswith("image/"))
async def handle_photo(message: types.Message, state: FSMContext):
    file_id = message.document.file_id  # Get file ID
    file_info = await bot.get_file(file_id)  # Get file info
    file_path = file_info.file_path  # Telegram's file path

    # 📥 Download the file
    image_data = await bot.download_file(file_path)

    save_input_path = f"{input_absolute_folder}{message.from_user.first_name}_input.jpg"
    with open(save_input_path, "wb") as new_file:
        new_file.write(image_data.read())

    await message.answer("Фото принято как файл. Теперь отправьте текст для фото.")
    await state.update_data(input_photo_path=absolute_path(save_input_path))
    await state.set_state(PostStates.photo_text)


# Handle invalid photo input
@dp.message(StateFilter(PostStates.uploading_photo))
async def invalid_photo(message: types.Message):
    await message.answer("❌ Отправьте фото, а не текст.", reply_markup=markup_cancelation())


# Handle photo text
@dp.message(StateFilter(PostStates.photo_text), F.text)
async def photo_text(message: types.Message, state: FSMContext):
    safe_text = hashed( message.text)
    safe_first_name = re.sub(r'[\/:*?"<>|]', '', message.from_user.first_name)
    print(f"Safe text:{safe_text}")
    print(f"message.text:{message.text}")

    data = await state.get_data()
    input_photo_path = data['input_photo_path']

    output_path_file = f"{output_absolute_folder}/{safe_first_name}_{safe_text}_edited.png"
    overlay_images(input_photo_path, frame_absolute_path, output_path_file, message.text)

    await state.update_data(output_photo_path=output_path_file)
    output_photo = FSInputFile(output_path_file)

    await message.answer_photo(output_photo)
    await message.answer("Хотите продолжить или попробовать еще раз?", reply_markup=inline_verification("photo_text"))


@dp.message(StateFilter(PostStates.photo_text))
async def invalid_text(message: types.Message, state: FSMContext):
    await message.answer("Вы должны отправить Текст")

# Handle post text
@dp.message(StateFilter(PostStates.post_text))
async def post_text(message: types.Message, state: FSMContext):
    await state.update_data(post_text=message.text)
    
    await message.answer(f'Текст для поста: "{message.text}"\nПродолжим или хотите поменять текст на другой?', reply_markup=inline_verification("post_text"))


@dp.message(F.document, F.document.mime_type == "application/pdf", StateFilter(PostStates.payment))
async def payment_handle_pdf(message: types.Message, state: FSMContext):
    await message.answer("✅ Ваш чек был принят. Если вы ошиблись, можете поменять файл перед тем как он будет сохранен и отправлен на обработку менеджера.",
                         reply_markup = inline_verification("payment"))    
    await state.update_data(receipt_id = message.document.file_id)
    await state.update_data(username=message.from_user.first_name)


@dp.message(F.photo, StateFilter(PostStates.payment))
async def payment_invalid_photo(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста отправьте чек в виду PDF файла. Фото чека не подойдет",
                         reply_markup = markup_cancelation()
                         )


@dp.message(StateFilter(PostStates.payment))
async def payment_invalid_rest(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста отправьте чек в виду PDF файла.", 
                         reply_markup = markup_cancelation()
                         )



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

                await call.message.edit_text(
                        f"Выберите дату публикации.",
                           reply_markup=create_calendar()
                           )
                await call.answer()
        elif step == "post_text":
            await state.set_state(PostStates.selecting_date)

            await call.message.edit_text(
                        f"Выберите дату публикации.",
                           reply_markup=create_calendar()
                           )
            await call.answer()


        elif step == "selecting_date":
            await state.set_state(PostStates.selecting_time)
            await call.message.edit_text("Теперь выберите время публикации.", reply_markup=build_hour_keyboard_clock())


        elif step == "selecting_time":
            await state.set_state(PostStates.final_verification)

            data = await state.get_data()

            post_text = data.get('post_text', None) 
            post_date = data.get('post_date')
            post_time = data.get('post_time')

            date_obj = datetime.strptime(post_date, "%Y-%m-%d")           
            formatted_date = f"{date_obj.year}, {date_obj.day} {months_ru[date_obj.month]}"

              
            if post_text: 
                post_text = f"Текст под постом: '{post_text}'\nДата: {formatted_date}\nВремя: {post_time}"
            else:
                post_text = f"Дата: {formatted_date}\nВремя: {post_time}"

            output_photo = FSInputFile(data['output_photo_path'])

            await call.message.answer_photo(output_photo, caption=post_text)

            await call.message.answer("Продолжим или если что-то хотите поменять начните заново", reply_markup=inline_verification("final_verification"))



        elif step == "final_verification":
            await call.message.answer("Оплатите 5 000тг через Kaspi номер: +7 705 406 60 26. После оплаты отправьте чек в виле PDF файла.", reply_markup = markup_cancelation()
                                      )
            await state.set_state(PostStates.payment)
        

        elif step == "payment":
            await call.message.answer("Поздравляю, вы зарегистрировали новый пост для рекламы. В скором времени менеджер обработает вашу заявку!.",
                                      reply_markup = markup_default())
                        
            data = await state.get_data()
            receipt_id = data.get("receipt_id")
            file_info = await bot.get_file(receipt_id)
            file_path = file_info.file_path
            pdf_data = await bot.download_file(file_path)

            to_hash = str(receipt_id) + str(call.message.message_id)
            save_random = hashed(to_hash)
            save_path = f"{receipts_absolute_folder}{data.get('username')}_{save_random}.pdf"

            with open(save_path, 'wb') as f:
                f.write(pdf_data.read())

            # Здесь должен быть код по сохранению данных в дб
            
            data = await state.get_data()
            user_id = call.message.chat.id
            username = call.message.from_user.username
            photo_path = data.get('output_photo_path')
            post_text = data.get('post_text', None)
            post_date = data.get('post_date')
            print(post_date)
            post_time = data.get('post_time')
            kaspi_path = save_path
            db.new_write(user_id, username, photo_path, post_text, post_date, post_time, kaspi_path)


            await state.clear()

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

            await call.message.edit_text(
                        f"Выберите дату публикации.",
                           reply_markup=create_calendar()
                           )
            await call.answer()



        elif step == "selecting_time":
            await state.set_state(PostStates.selecting_time)
            await call.message.edit_text("Выберите новое время публикации.", reply_markup=build_hour_keyboard_clock())


        elif step == "final_verification":
            await state.set_state(PostStates.uploading_photo)
            await call.message.answer("Отправьте, пожалуйста, новое фото для поста.", reply_markup=markup_cancelation())
        
        elif step == "payment":
            await state.set_state(PostStates.payment)
            await call.message.answer("Отправьте пожалуйста новый чек.")


    await call.answer()

# Handle calendar callback
@dp.callback_query(F.data.startswith("date_"), StateFilter(PostStates.selecting_date))
async def selecting_date(callback: types.CallbackQuery, state: FSMContext):
    selected_date = callback.data.replace("date_", "")
    
    date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
    formatted_date = f"{date_obj.year}, {date_obj.day} {months_ru[date_obj.month]}"

    await state.update_data(post_date=selected_date)
    print("In callback of calendar")
    print(selected_date)
    data = await state.get_data()
    print(data.get('post_date'))

    await callback.message.edit_text(
            f'Вы выбрали {formatted_date}.\nВы можете поменять дату если ошиблись.',
            reply_markup = inline_verification("selecting_date")
        )
    await callback.answer()     



@dp.callback_query(F.data.startswith("hour_") | (F.data == "none"), StateFilter(PostStates.selecting_time))
async def callback_inline(call: types.CallbackQuery, state: FSMContext):
    data = call.data

    if data.startswith("hour_"):
        chosen_hour = data.split("_")[1]
        await state.update_data(post_time = chosen_hour)
        # ✅ Edit message text to show the selected hour
        await call.message.edit_text(f"Выбранное время: {chosen_hour}. Если вы можете поменять время если ошиблись.",
                                     reply_markup = inline_verification("selecting_time")
                                     )

    await call.answer()  # ✅ Always close the callback query to avoid "loading" state

# Start polling
if __name__ == '__main__':
    dp.run_polling(bot)
