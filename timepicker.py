import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import bot_token
API_TOKEN = bot_token
bot = telebot.TeleBot(API_TOKEN)

user_data = {}  # For storing user-selected hours temporarily

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def build_hour_keyboard_clock_style() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    
    # This 2D list represents the 'shape' of the clock
    clock_layout = [
        [0,  0,  0, 12, 0,  0,  0],
        [0,  0, 11,  0, 13,  0,  0],
        [0, 10,  0,  0, 0,  14,  0],
        [9,  0,  0,  0, 0,  0,  15],
        [0,  8,  0,  0, 0,  16,  0],
        [0,  0,  7,  0, 17,  0,  0],
        [0,  0,  0,  18, 0,  0,  0]
    ]

    for row in clock_layout:
        buttons = []
        for cell in row:
            if cell == 0:
                # Blank button to keep the shape
                buttons.append(InlineKeyboardButton(" ", callback_data="none"))
            else:
                # Hour button
                string_cell = str(cell)
                string_cell += ":00"
                buttons.append(InlineKeyboardButton(
                    string_cell,
                    callback_data=f"hour_{string_cell}"
                ))
        # Add this row of 7 buttons to the markup
        markup.row(*buttons)
    
    return markup


@bot.message_handler(commands=['picktime'])
def pick_time(message):
    hour_keyboard = build_hour_keyboard_clock_style()
    bot.send_message(
        chat_id=message.chat.id,
        text="Choose the hour:",
        reply_markup=hour_keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('hour_') or call.data == ("none"))
def callback_inline(call):
    data = call.data
    
    if data.startswith("hour_"):
        chosen_hour = data.split("_")[1]
        user_data[call.from_user.id] = {"hour": chosen_hour}
        
        minute_keyboard = build_minute_keyboard()
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"Hour chosen: {chosen_hour}"
        )
        bot.answer_callback_query(call.id)



bot.infinity_polling()

