from config import manager_bot_token

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


bot = Bot(token=user_bot_token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)



@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(f"Здравствуйте {message.from_user.first_name}, добро пожаловать!", reply_markup=markup_default())
