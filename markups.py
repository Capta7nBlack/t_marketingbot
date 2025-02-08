from telebot import types

# 
def markup_default():
    markup= types.ReplyKeyboardMarkup(resize_keyboard=True)
    Create = types.KeyboardButton('Создать рекламный пост')
    Showall = types.KeyboardButton('Показать все созданные посты')
    markup.row(Create, Showall)
    return markup

def markup_verification():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    Proceed = types.KeyboardButton('Продолжить')
    Cancel = types.KeyboardButton('Начать создание поста сначало')
    markup.row(Proceed,Cancel)
    return markup
