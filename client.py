from telebot import TeleBot

import db

import re

from datetime import date
from dateutil.relativedelta import relativedelta
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from timepicker import build_hour_keyboard_clock

from get_absolute_path import absolute_path
from imageloading.imagemaker import overlay_images
from imageloading.image_typeless_loader import typeless_loader
from config import frame_absolute_path
from config import output_absolute_folder
from telebot import types

from config import under_post_text_switch

from markups import markup_default, markup_verification

from config import bot_token
bot = TeleBot(bot_token)

try:
    db.create()
except Exception as e:
    print(e)

@bot.message_handler(commands=['start'])
def start(m):
        bot.send_message(m.chat.id,
                     f"Здравствуйте { m.from_user.first_name}, вас приветствует бот по приему рекламных заявок в инстаграм. Нажмите кнопку создать рекламный пост, если хотите купить рекламу. Чтобы выйти из диалогового окна, нажмите 'Остановить диалог'",
                     reply_markup = markup_default()) 


@bot.message_handler(func=lambda message: message.text == 'Показать все созданные посты')
def show_posts(m):
    bot.send_message(m.chat.id,
                     f"wanna show you all")

@bot.message_handler(func=lambda message: message.text == 'Создать рекламный пост')
def create_post(m):
    try:
        db.temporary_delete(m.chat.id)
    except Exception as e:
        print(e)
    data = {}
    bot.send_message(m.chat.id,
                     f"Отправьте фото для поста.",
                     reply_markup = markup_verification())
    bot.register_next_step_handler(m, photo_handler, data)

def photo_handler(m, data):
    if m.content_type != 'photo':
        if m.text == "Остановить диалог":
            bot.send_message(m.chat.id, 
                             f"Диалог прекращен",
                             reply_markup = markup_default())
            try:
                db.temporary_delete(m.chat.id)
            except Exception as e:
                print(e)

            return
        # Inform the user that a photo is required and re-register the handler
        msg = bot.send_message(m.chat.id, "Вы отправили не фото. Пожалуйста отправьте Фото", reply_markup = markup_verification())
        bot.register_next_step_handler(m, photo_handler, data)
        return

    file_id = m.photo[-1].file_id
    # Retrieve file info from Telegram servers
    file_info = bot.get_file(file_id)
    # Download the file using the file path from file_info
    downloaded_file = bot.download_file(file_info.file_path)

    # Save the image to disk (or process it as needed)
    save_input_path = f"imageloading/user_input_photos/{m.from_user.first_name}_input.jpg"
    with open(save_input_path, "wb") as new_file:
        new_file.write(downloaded_file)
    bot.send_message(m.chat.id, f"Фото принято и обрабатывается. Пожалуйста отправьте текст для помещения на фото.", reply_markup = None)
    data['input_photo_path'] = absolute_path(save_input_path)
    bot.register_next_step_handler(m, photo_text_handler, data)

def photo_text_handler(m, data):
    if m.text == "Остановить диалог":
        bot.send_message(m.chat.id, 
                             f"Диалог прекращен",
                             reply_markup = markup_default())
        try:
            db.temporary_delete(m.chat.id)
        except Exception as e:
            print(e)

        return

    absolute_input_path = data.get('input_photo_path')
    if "\\" in m.text:
        msg = bot.send_message(m.chat.id, "Пожалуйста не используйте '\\'")

        bot.register_next_step_handler(msg, photo_text_handler, data)
        return

    safe_text = re.sub(r'[\/:*?"<>|]', '', m.text)
    safe_first_name =  re.sub(r'[\/:*?"<>|]', '', m.from_user.first_name)
    output_path_file = output_absolute_folder + f"/{safe_first_name}_{safe_text}_edited.png"
    overlay_images(absolute_input_path, frame_absolute_path, output_path_file, m.text) 
    
    if under_post_text_switch:
        bot.send_message(m.chat.id,
                    f"Отправьте текст который будет под постом."
                     )
        data['output_photo_path'] = output_path_file
        bot.register_next_step_handler(m, post_text_handler, data)
    else:

        with open(output_path_file, "rb") as photo:

            bot.send_photo(m.chat.id, photo)
        
        bot.send_message(m.chat.id,
                     f"Это то, как будет выглядеть ваш пост. Если вам хотите изменить фото или текст, начните процесс сначалo.",
                         reply_markup = markup_verification()
                     )
        data['output_photo_path'] = output_path_file
        data['post_text'] = None
        bot.register_next_step_handler(m,verification_handler, data)

def post_text_handler(m, data):
    if m.text == "Остановить диалог":
        bot.send_message(m.chat.id, 
                             f"Диалог прекращен",
                             reply_markup = markup_default())
        try:
            db.temporary_delete(m.chat.id)
        except Exception as e:
            print(e)

        return

    photo_path = data.get('output_photo_path')
    with open(photo_path, "rb") as photo:
        bot.send_photo(m.chat.id, photo, caption = m.text)

    bot.send_message(m.chat.id,
                     f"Это то, как будет выглядеть ваш пост. Если вам хотите изменить фото или текст, начните процесс сначал.",
                     reply_markup = markup_verification()
                     )
    data['post_text'] = m.text
    bot.register_next_step_handler(m, verification_handler, data)

def verification_handler(m, data):
    if m.text == "Продолжить":
        calendar, step = DetailedTelegramCalendar(locale="ru", min_date = date.today(), max_date = date.today() + relativedelta(months=1)).build()
        bot.send_message(m.chat.id,
                     f"Выберите дату выпуска поста.",
                     reply_markup=calendar)
        user_id = m.chat.id
        photo_path = data.get('output_photo_path')
        post_text = None
        if under_post_text_switch:
            post_text = data.get('post_text')
        try:
            db.temporary_write(user_id, photo_path, post_text)
        except Exception as e:
            print("Catched exception:", e)

    elif m.text == "Остановить диалог":
        bot.send_message(m.chat.id, 
                             f"Диалог прекращен",
                             reply_markup = markup_default())
        try:
            db.temporary_delete(m.chat.id)
        except Exception as e:
            print(e)

            return
        data = {}
        bot.register_next_step_handler(m, photo_handler, data)

def timepick_handler(m, date):
    if m.text == "Остановить диалог":
        bot.send_message(m.chat.id,
                     f"Отправьте фото для поста.",
                         reply_markup = markup_default())
        try:
            db.temporary_delete(m.chat.id)
        except Exception as e:
            print(e)

        return
    db.temporary_write_date(m.chat.id, date)
    bot.send_message(m.chat.id, 
                    f"Выберите время для выпуска поста.",
                    reply_markup = timepicker
                    )

def final_verif(m, data):
    if m.text == "Продолжить":
        bot.send_message(m.chat.id,
                         f"Оплатите по 5к по номеру +7 705 111 11 11, после чего отправьте пдф каспи чека сюда.")
    elif m.text == "Остановить диалог":
        bot.send_message(m.chat.id,
                     f"Отправьте фото для поста.",
                         reply_markup = markup_default())
        try:
            db.temporary_delete(m.chat.id)
        except Exception as e:
            print(e)
        return
        data = {}
        bot.register_next_step_handler(m, photo_handler, data)




@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def calendar_proceed(c):
    result, key, step = DetailedTelegramCalendar(locale="ru", min_date = date.today(), max_date = date.today() + relativedelta(months=1)).process(c.data)
    if not result and key:
        bot.edit_message_text(f"Выберите дату публикации",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Вы хотите опубликовать пост {result}",
                              c.message.chat.id,
                              c.message.message_id)
        
        db.temporary_write_date(c.message.chat.id, result)
        timepicker = build_hour_keyboard_clock()
        msg = bot.send_message(c.message.chat.id, 
                    f"Выберите время для выпуска поста.",
                    reply_markup = timepicker
                    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('hour_'))
def timepicker_proceed(call):
    data = call.data
    
    if data.startswith("hour_"):
        chosen_hour = data.split("_")[1]
        
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"Hour chosen: {chosen_hour}"
        )
        bot.answer_callback_query(call.id)
        
        verif(msg,chosen_hour)


def verif(m, chosen_hour):
    if m.text == "Остановить диалог":
        bot.send_message(m.chat.id, 
                         f"Диалог прекращен",
                         reply_markup = markup_default())
        try:
            db.temporary_delete(m.chat.id)
        except Exception as e:
            print(e)

    data = db.temporary_read(m.chat.id)
    photo_path = data[0]
    post_text = data[1]
    date = data[2]
    temp_dict = {
            'photo_path':photo_path,
            'post_text':post_text,
            'post_date':date,
            'post_time':chosen_hour
            }
    if post_text:

        post_text += "\nДата: " + str(date)
        post_text += "\nВремя: " + str(chosen_hour)

    else:
        post_text = ""
        post_text += "\nДата: " + str(date)
        post_text += "\nВремя: " + str(chosen_hour)

    with open(photo_path, 'rb') as photo:
        bot.send_photo(m.chat.id, photo, caption = post_text)
    msg = bot.send_message(m.chat.id,
                     f"Все ли вас устраивает? Если нет, процесс нужно начать сначало. Для этого остановите диалог и начните его заново",
                     reply_markup = markup_verification()
                     )
    bot.register_next_step_handler(msg, final_verif, temp_dict)           



bot.polling()
