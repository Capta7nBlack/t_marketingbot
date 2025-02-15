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

from modules.text import text_buttons, text_message_basic, text_message_photo, text_message_post_text
from modules.text import text_message_calendar, text_message_time_picker, text_message_payment
from modules.text import text_message_showall, text_message_verification

from imageloading.imageprocesser import overlay_images

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
@dp.message(F.text == text_buttons.get("cancelation"))
async def cancel_conversation(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(text_message_basic.get("cancelation"), reply_markup=markup_default())

# Start command handler
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(text_message_basic.get('start'),
                         reply_markup=markup_default()
                         )

# Create post handler
@dp.message(F.text == text_buttons.get('default_create'))
async def default_create(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(PostStates.uploading_photo)
    await message.answer(text_message_basic.get("default_create"), reply_markup=markup_cancelation())

# Show all posts handler
@dp.message(F.text == text_buttons.get('default_showall'))
async def default_showall(message: types.Message, state: FSMContext):
    await state.clear()

    data = db.show_all(message.chat.id)
    i = 1
    if data:
        for photo_path, post_text, post_date, post_time, kaspi_path in data:
            date_obj = datetime.strptime(post_date, "%Y-%m-%d")           
            formatted_date = f"{date_obj.year}, {date_obj.day} {months_ru[date_obj.month]}"
            
            # Use the refactored dictionary for showall_post
            caption = text_message_showall["showall_post"](post_text, formatted_date, post_time)
            distance = text_message_showall.get("showall_distance")

            output_photo = FSInputFile(photo_path)
            pdf_file = FSInputFile(kaspi_path)

            await message.answer(text_message_showall["showall_post_number"](i))
            i += 1  # Increment post number
            await message.answer_photo(output_photo, caption=caption)
            await message.answer_document(pdf_file, caption=distance)

        await message.answer(text_message_showall["showall_manager"](admin_telegram))
    else:
        await message.answer(text_message_showall.get("showall_empty"), reply_markup=markup_default())

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

    await message.answer(text_message_photo.get("photo_uploaded"))
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

    await message.answer(text_message_photo.get("photo_uploaded_as_file"),
                         reply_markup=markup_cancelation()
                         )
    await state.update_data(input_photo_path=absolute_path(save_input_path))
    await state.set_state(PostStates.photo_text)


# Handle invalid photo input
@dp.message(StateFilter(PostStates.uploading_photo))
async def invalid_photo(message: types.Message):
    await message.answer(text_message_photo.get("invalid_photo"), reply_markup=markup_cancelation())
    

# Handle photo text
@dp.message(StateFilter(PostStates.photo_text), F.text)
async def photo_text(message: types.Message, state: FSMContext):
    safe_text = hashed( message.text)
    safe_first_name = re.sub(r'[\/:*?"<>|]', '', message.from_user.first_name)

    data = await state.get_data()
    input_photo_path = data['input_photo_path']

    output_path_file = f"{output_absolute_folder}/{safe_first_name}_{safe_text}_edited.png"
    overlay_images(input_photo_path, frame_absolute_path, output_path_file, message.text)

    await state.update_data(output_photo_path=output_path_file)
    output_photo = FSInputFile(output_path_file)

    await message.answer_photo(output_photo)
    await message.answer(text_message_photo.get('edited_photo_verification'),
                         reply_markup=inline_verification("photo_text")
                         )


@dp.message(StateFilter(PostStates.photo_text))
async def invalid_text(message: types.Message, state: FSMContext):
    await message.answer(text_message_photo.get("invalid_text"))
    
    
# Handle post text
@dp.message(StateFilter(PostStates.post_text))
async def post_text(message: types.Message, state: FSMContext):
    await state.update_data(post_text=message.text)
    
    await message.answer(text_message_post_text["post_text_received"](message.text),
                         reply_markup=inline_verification("post_text")
                         )


@dp.message(F.document, F.document.mime_type == "application/pdf", StateFilter(PostStates.payment))
async def payment_handle_pdf(message: types.Message, state: FSMContext):
    await message.answer(text_message_payment.get("payment_handle_pdf"),
                         reply_markup = inline_verification("payment"))    
    await state.update_data(receipt_id = message.document.file_id)
    await state.update_data(username=message.from_user.first_name)


@dp.message(F.photo, StateFilter(PostStates.payment))
async def payment_invalid_photo(message: types.Message, state: FSMContext):
    await message.answer(text_message_payment.get("payment_invalid_photo"),
                         reply_markup = markup_cancelation()
                         )


@dp.message(StateFilter(PostStates.payment))
async def payment_invalid_rest(message: types.Message, state: FSMContext):
    await message.answer(text_message_payment.get("payment_invalid_rest"), 
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
                await call.message.answer(
                        text_message_verification.get("confirm_photo_text__ask_post_text"),
                        reply_markup=markup_cancelation()
                                         )
            else:
                await state.set_state(PostStates.selecting_date)

                await call.message.edit_text(
                    text_message_verification.get("confirm_photo_text_no_post_text__ask_date"),
                    reply_markup=create_calendar()
                                            )
                await call.answer()
        elif step == "post_text":
            await state.set_state(PostStates.selecting_date)

            await call.message.edit_text(
                        text_message_verification.get("confirm_post_text__ask_date"),
                           reply_markup=create_calendar()
                           )
            await call.answer()


        elif step == "selecting_date":
            await state.set_state(PostStates.selecting_time)
            await call.message.edit_text(
                    text_message_verification.get("confirm_selecting_date__ask_time"),
                    reply_markup=build_hour_keyboard_clock()
                                         )


        elif step == "selecting_time":
            await state.set_state(PostStates.final_verification)

            data = await state.get_data()

            post_text = data.get('post_text', None) 
            post_date = data.get('post_date')
            post_time = data.get('post_time')

            date_obj = datetime.strptime(post_date, "%Y-%m-%d")           
            formatted_date = f"{date_obj.year}, {date_obj.day} {months_ru[date_obj.month]}"

              
            caption = text_message_verification.get("confirm_selecting_time__show_post")(post_text, formatted_date, post_time)

            output_photo = FSInputFile(data['output_photo_path'])

            await call.message.answer_photo(output_photo, caption=caption)

            await call.message.answer(text_message_verification.get("confirm_selecting_time__final_verification"), reply_markup=inline_verification("final_verification"))



        elif step == "final_verification":
            await call.message.answer(text_message_verification.get("confirm_final_verification__ask_pdf"), reply_markup = markup_cancelation()
                                      )
            await state.set_state(PostStates.payment)
        

        elif step == "payment":
            await call.message.answer(text_message_verification.get("confirm_payment__success"),
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
            input_photo_path = data.get('input_photo_path')
            photo_path = data.get('output_photo_path')
            post_text = data.get('post_text', None)
            post_date = data.get('post_date')
            print(post_date)
            post_time = data.get('post_time')
            kaspi_path = save_path
            db.new_write(user_id, username,input_photo_path, photo_path, post_text, post_date, post_time, kaspi_path)


            await state.clear()

    elif call.data.startswith("retry_"):
        if step == "photo_text":
            await state.set_state(PostStates.uploading_photo)
            await call.message.answer(text_message_verification.get("retry_photo_text"), reply_markup=markup_cancelation())


        elif step == "post_text":
            await call.answer()
            await state.set_state(PostStates.post_text)
            await call.message.answer(text_message_verification.get("retry_post_text"), reply_markup=markup_cancelation())


        elif step == "selecting_date":

            await state.set_state(PostStates.selecting_date)

            await call.message.edit_text(
                        text_message_verification.get("retry_selecting_date"),
                           reply_markup=create_calendar()
                           )
            await call.answer()



        elif step == "selecting_time":
            await state.set_state(PostStates.selecting_time)
            await call.message.edit_text(text_message_verification.get("retry_selecting_time"), reply_markup=build_hour_keyboard_clock())


        elif step == "final_verification":
            await state.set_state(PostStates.uploading_photo)
            await call.message.answer(text_message_verification.get("retry_final_verification"), reply_markup=markup_cancelation())
        
        elif step == "payment":
            await state.set_state(PostStates.payment)
            await call.message.answer(text_message_verification.get("retry_payment"))


    await call.answer()

# Handle calendar callback
@dp.callback_query(F.data.startswith("date_"), StateFilter(PostStates.selecting_date))
async def selecting_date(callback: types.CallbackQuery, state: FSMContext):
    selected_date = callback.data.replace("date_", "")
    
    date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
    formatted_date = f"{date_obj.year}, {date_obj.day} {months_ru[date_obj.month]}"

    await state.update_data(post_date=selected_date)
    
    
    data = await state.get_data()
    

    await callback.message.edit_text(
            text_message_calendar.get("calendar_date_selected")(formatted_date),
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
        await call.message.edit_text(text_message_time_picker.get("time_picker_time_selected")(chosen_hour),
                                     reply_markup = inline_verification("selecting_time")
                                     )

    await call.answer()  # ✅ Always close the callback query to avoid "loading" state

# Start polling
if __name__ == '__main__':
    dp.run_polling(bot)
