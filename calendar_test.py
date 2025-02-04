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

# calendar, step = DetailedTelegramCalendar(locale="ru", min_date = date.today(), max_date = date.today() + relativedelta(months=1)).build()
   # bot.send_message(m.chat.id,
   #                  f"Выберите дату публикации",
   #
