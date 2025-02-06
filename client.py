from telebot import TeleBot

from datetime import date
from dateutil.relativedelta import relativedelta
# from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from get_absolute_path import absolute_path
from imageloading.imagemaker import overlay_images
from imageloading.image_typeless_loader import typeless_loader
from config import frame_absolute_path
from config import output_absolute_folder
from telebot import types


from config import bot_token
bot = TeleBot(bot_token)

#min_date = date.today()), max_date = datetime.now() + relativedelta(months=1)
@bot.message_handler(commands=['start'])
def start(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    Create = types.KeyboardButton('Создать рекламный пост')
    Showall = types.KeyboardButton('Показать все созданные посты')
    markup.row(Create, Showall)
    bot.send_message(m.chat.id,
                     f"Здравствуйте { m.from_user.first_name}, вас приветствует бот по приему рекламных заявок в инстаграм. Нажмите кнопку создать рекламный пост, если хотите.",
                     reply_markup = markup) 


@bot.message_handler(func=lambda message: message.text == 'Создать рекламный пост')
def create_post(m):
    bot.send_message(m.chat.id,
                     f"Отправьте фото для поста.")
    bot.register_next_step_handler(m, photo_handler)

def photo_handler(m):
    if m.content_type != 'photo':
        # Inform the user that a photo is required and re-register the handler
        msg = bot.send_message(m.chat.id, "Пожалуйста отправьте Фото.")
        bot.register_next_step_handler(msg, photo_handler)
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
    bot.register_next_step_handler(m, lambda m: photo_text_handler(m, path = absolute_path(save_input_path)))

def photo_text_handler(m, path):
    absolute_input_path = path
    if m.content_type != 'text':
        # Inform the user that a photo is required and re-register the handler
        msg = bot.send_message(m.chat.id, "Пожалуйста отправьте Текст")

        bot.register_next_step_handler(msg, lambda m: photo_text_handler(m, path = save_path))
        return
    output_path_file = output_absolute_folder + f"/{m.from_user.first_name}_{m.text}_edited.png"
    print(absolute_path("imageloading/frame.png"))
    overlay_images(absolute_input_path, frame_absolute_path, output_path_file, m.text) 



bot.polling()
