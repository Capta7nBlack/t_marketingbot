from config import manager_bot_token, allowed_users
from modules.markup_states import markup_manager_default


from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import text
from aiogram.filters.callback_data import CallbackData

from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, get_user_locale



bot = Bot(token=manager_bot_token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)



class Authorization(StatesGroup):
    authorized = State()

@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    username = message.from_user.username  # Get the sender's username
    print(username)
    
    if username in allowed_users or "@" + username in allowed_users or username[1:] in allowed_users:
        await state.set_state(Authorization.authorized)
        await message.reply(f"Welcome, {username}! You are authorized. ✅",
                            reply_markup = markup_manager_default()
                            )
    else:
        await message.reply("❌ You are not authorized to use this bot.")


# @dp.message(StateFilter(Authorized.authorized))





if __name__ == '__main__':
    dp.run_polling(bot)
