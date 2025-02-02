from telebot import TeleBot

from datetime import date
from dateutil.relativedelta import relativedelta

from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from config import bot_token
bot = TeleBot(bot_token)

#min_date = date.today()), max_date = datetime.now() + relativedelta(months=1)
@bot.message_handler(commands=['start'])
def start(m):
    calendar, step = DetailedTelegramCalendar(locale="ru", min_date = date.today(), max_date = date.today() + relativedelta(months=1)).build()
    bot.send_message(m.chat.id,
                     f"Выберите дату публикации",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
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
