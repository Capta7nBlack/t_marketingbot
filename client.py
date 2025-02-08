from telebot import TeleBot

import re

from datetime import date
from dateutil.relativedelta import relativedelta
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP


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


#min_date = date.today()), max_date = datetime.now() + relativedelta(months=1)
@bot.message_handler(commands=['start'])
def start(m):
        bot.send_message(m.chat.id,
                     f"Здравствуйте { m.from_user.first_name}, вас приветствует бот по приему рекламных заявок в инстаграм. Нажмите кнопку создать рекламный пост, если хотите.",
                     reply_markup = markup_default()) 


@bot.message_handler(func=lambda message: message.text == 'Создать рекламный пост')
def create_post(m):
    data = {}
    bot.send_message(m.chat.id,
                     f"Отправьте фото для поста.")
    bot.register_next_step_handler(m, photo_handler, data)

def photo_handler(m, data):
    if m.content_type != 'photo':
        # Inform the user that a photo is required and re-register the handler
        msg = bot.send_message(m.chat.id, "Пожалуйста отправьте Фото.")
        bot.register_next_step_handler(msg, photo_handler, data)
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
    bot.send_message(m.chat.id, f"Фото принято и обрабатывается. Пожалуйста отправьте текст для помещения на фото.")
    data['input_photo_path'] = absolute_path(save_input_path)
    bot.register_next_step_handler(m, photo_text_handler, data)

def photo_text_handler(m, data):

    absolute_input_path = data.get('input_photo_path')
    if m.content_type != 'text':
        # Inform the user that a photo is required and re-register the handler
        msg = bot.send_message(m.chat.id, "Пожалуйста отправьте Текст")

        bot.register_next_step_handler(msg, photo_text_handler, data)
        return
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
    elif m.text == "Начать создание поста сначало":
        bot.send_message(m.chat.id,
                     f"Отправьте фото для поста.",
                         reply_markup = markup_default())
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

bot.polling()
