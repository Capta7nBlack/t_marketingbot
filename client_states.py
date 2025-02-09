import telebot

import re

from datetime import date
from dateutil.relativedelta import relativedelta
from telegram_bot_calendar import DetailedTelegramCalendar
from timepicker import build_hour_keyboard_clock

from imageloading.imagemaker import overlay_images
from imageloading.image_typeless_loader import typeless_loader

from telebot import TeleBot, types
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup
from telebot.states.sync.context import StateContext

from get_absolute_path import absolute_path

from markups import markup_default, inline_verification, markup_cancelation

from config import frame_absolute_path, output_absolute_folder, bot_token, under_post_text_switch

storage = StateMemoryStorage()
bot = TeleBot(bot_token, state_storage=storage)



class PostStates(StatesGroup):
    uploading_photo = State()
    photo_text = State()
    post_text = State()
    selecting_date = State()
    selecting_time = State()
    final_verification = State()
    payment = State()


@bot.message_handler(func=lambda message: message.text == "❌ Остановить диалог", state="*")
def cancel_conversation(message):
    bot.delete_state(message.chat.id)  # Reset user state
    bot.send_message(
        message.chat.id, 
        "❌ Диалог прекращен. Вы можете начать заново", 
        reply_markup=markup_default()  # Return to the main menu keyboard
    )







@bot.message_handler(commands=['start'])
def start(message: types.Message):
    bot.send_message(
        message.chat.id, 
        f"Здравствуйте {message.from_user.first_name}, добро пожаловать!", 
        reply_markup=markup_default()
    )




@bot.message_handler(func=lambda message: message.text == "Создать рекламный пост", state = None)
def default_create(message: types.Message):
    
    
    bot.set_state(message.chat.id, PostStates.uploading_photo)  # Correctly set the state
    bot.send_message(message.chat.id, "Отправьте, пожалуйста, фото для поста.", reply_markup=markup_cancelation())

    state = bot.get_state(message.chat.id)

    print(f"🟢 State after setting: {state}") 

@bot.message_handler(func=lambda message: message.text == "Показать все созданные посты", state = None)
def default_showall(message):
    bot.delete_state(message.chat.id)  # Ensure no state is active

    bot.send_message(message.chat.id,
                     f"This part of the bot is work in progress"
                     )



@bot.message_handler(state=PostStates.uploading_photo, content_types=['photo'])
def handle_photo(message):
    print("Handle photo triggered")
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    save_input_path = f"imageloading/user_input_photos/{message.from_user.first_name}_input.jpg"
    with open(save_input_path, "wb") as new_file:
        new_file.write(downloaded_file)

    bot.send_message(message.chat.id, "Фото принято. Теперь отправьте текст для фото.")
    
    with bot.retrieve_data(message.chat.id) as data:
        data['input_photo_path'] = absolute_path(save_input_path)

    bot.set_state(message.chat.id, PostStates.photo_text)

# Handle invalid photo input
@bot.message_handler(state=PostStates.uploading_photo)
def invalid_photo(message):
    bot.send_message(message.chat.id, "❌ Отправьте фото, а не текст.", reply_markup=markup_cancelation())

@bot.message_handler(func=lambda message: True, content_types=['photo'])
def debug_state(message):
    current_state = bot.get_state(message.chat.id)
    print(f"🔍 Current state: {current_state}")




@bot.message_handler(state=PostStates.photo_text)
def photo_text(message):
    safe_text = re.sub(r'[\/:*?"<>|]', '', message.text)
    safe_first_name = re.sub(r'[\/:*?"<>|]', '', message.from_user.first_name)

    with bot.retrieve_data(message.chat.id) as data:
        input_photo_path = data['input_photo_path']

        output_path_file = f"{output_absolute_folder}/{safe_first_name}_{safe_text}_edited.png"
        overlay_images(input_photo_path, frame_absolute_path, output_path_file, message.text)

        data['output_photo_path'] = output_path_file
    

    with open(output_path_file, 'rb') as photo:
        bot.send_photo(photo)
    bot.send_message(message.chat.id, 
                     f"Хотите продолжить или попробовать еще раз?",
                     reply_markup = inline_verification(photo_text)
                     )


@bot.message_handler(state=PostStates.post_text)
def post_text(message):
    with bot.retrieve_data(message.chat.id) as data:
        data['post_text'] = message.text
    bot.send_message(message.chat.id, 
                     f"Продолжим или хотите поменять текст на другой?",
                     reply_markup = inline_verification(post_text)
                     )

@bot.callback_query_handler(func=lambda call: call.data.startswith(("confirm_", "retry_")), state="*")
def handle_verification(call):
    step = call.data.split("_")[1]  # Extract the step name
    
    if call.data.startswith("confirm_"):
        if step == "photo_text":
            if under_post_text_switch:
                bot.set_state(call.message.chat.id, PostStates.post_text)
                bot.send_message(call.message.chat.id, 
                                 f"Отправьте текст для поста",
                                 reply_markup = markup_cancelation()
                                 )
            else:
                bot.set_state(call.message.chat.id, PostStates.selecting_date)
                bot.send_message(call.message.chat.id,
                                     "Выберите дату публикации.",
                                     reply_markup=DetailedTelegramCalendar(locale="ru", min_date=date.today(), max_date=date.today() + relativedelta(months=1)).build()
                                     )
        elif step == "post_text":
            bot.set_state(call.message.chat.id, PostStates.selecting_date)
            bot.send_message(call.message.chat.id,
                                     "Выберите дату публикации.",
                                     reply_markup=DetailedTelegramCalendar(locale="ru", min_date=date.today(), max_date=date.today() + relativedelta(months=1)).build()
                                     )

        elif step == "selecting_date":
            bot.set_state(call.message.chat.id, PostStates.selecting_time)
            bot.edit_message_text(f"Теперь выберите время публикации.",
                                  call.message.chat.id, call.message.message_id, reply_markup=build_hour_keyboard_clock()
                                  )

        elif step == "selecting_time":
            bot.set_state(call.message.chat.id, PostStates.final_verification)

            with bot.retrieve_data(call.message.chat.id) as data:
                if under_post_text_switch:
                    post_text = f"{data['post_text']}\nДата: {data['post_date']}\nВремя: {data['post_time']}"
                else:
                    post_text = f"Дата: {data['post_date']}\nВремя: {data['post_time']}"

                with open(data['output_photo_path'], 'rb') as photo:
                    bot.send_photo(call.message.chat.id, photo, caption=post_text)  

            bot.send_message(call.message.chat.id,
                            f"Продолжим или если что-то хотите поменять начните заново",
                             reply_markup = inline_verification(final_verification)
                             )

    elif call.data.startswith("retry_"):
        if step == "photo_text":
            bot.set_state(call.message.chat.id, PostStates.uploading_photo) 
            bot.edit_message(f"Пожалуйста отправьте фото заново",
                             call.message.chat.id,
                             call.message.message_id,
                             reply_markup = inline_verification(photo_text)
                             )
        elif step == "post_text":
            bot.set_state(call.message.chat.id, PostStates.post_text)
            bot.edit_message(f"Пожалуйста отправьте новый текст",
                             call.message.chat.id,
                             call.message.message_id,
                             reply_markup = inline_verification(post_text)
                             )



        elif step == "selecting_date":
            bot.set_state(call.message.chat.id, PostStates.selecting_date)
            bot.edit_message(f"Выберите дату публикации.",
                                     call.message.chat.id,
                                     call.message.message_id,
                                     reply_markup=DetailedTelegramCalendar(locale="ru", min_date=date.today(), max_date=date.today() + relativedelta(months=1)).build()
                                     )
        elif step == "selecting_time":
            bot.set_state(call.message.chat.id, PostStates.selecting_time)
            bot.edit_message_text(f"Выберите время публикации.",
                                  call.message.chat.id, call.message.message_id, reply_markup=build_hour_keyboard_clock()
                                  )



    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func = DetailedTelegramCalendar.func(), state=PostStates.selecting_date)
def selecting_date(call):
    result, key, step = DetailedTelegramCalendar(locale="ru", min_date=date.today(), max_date=date.today() + relativedelta(months=1)).process(call.data)

    if not result and key:
        bot.edit_message_text("Выберите дату публикации", call.message.chat.id, call.message.message_id, reply_markup=key)
    elif result:
        with bot.retrieve_data(call.message.chat.id) as data:
            data['post_date'] = result

        bot.edit_message_text(f"Вы выбрали {result}. Хотите продолжить или выбрать дату заново?",
                              call.message.chat.id, call.message.message_id, reply_markup=inline_verification(selecting_date))
        bot.set_state(call.message.chat.id, PostStates.selecting_time)



@bot.callback_query_handler(func= lambda call: call.data.startswith('hour_'), state=PostStates.selecting_time)
def selecting_time(call):
    chosen_hour = call.data.split("_")[1]
    with bot.retrieve_data(call.message.chat.id) as data:
        data['post_time'] = chosen_hour

    bot.edit_message_text(f"Вы выбрали {chosen_hour}. Продолжим или хотите выбрать время выпуска заново?",
                          call.message.chat.id, call.message.message_id, reply_markup=inline_verification(selecting_time)
                          )


bot.polling()
