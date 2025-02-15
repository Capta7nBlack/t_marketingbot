import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import price, kaspi_number


# NO FIELD CAN HAVE NONE VALUE, UNLESS MENTIONED, since telegram does not allow to send empty messages

text_buttons = {
        "default_create":"Создать рекламный пост",
        "default_showall":"Показать все созданные посты",
        "verification_confirm":"✅ Подтвердить",
        "verification_retry":"🔄 Повторить",
        "cancelation":"❌ Остановить диалог"
          }


text_message_basic = {
    "cancelation": "❌ Диалог прекращен. Вы можете начать заново",
    "start": "Здравствуйте, добро пожаловать!",
    "default_create": "Отправьте, пожалуйста, фото для поста.",
}

text_message_showall = {
    "showall_post": lambda post_text, formatted_date, post_time: (
        f"Текст под постом: '{post_text}'\nДата: {formatted_date}\nВремя: {post_time}"
        if post_text
        else f"Дата: {formatted_date}\nВремя: {post_time}"
    ),
    "showall_distance": "\n---\n---\n---",
    "showall_post_number": lambda post_number: f"Пост номер: {post_number}",
    "showall_manager": lambda manager_telegram: f"Если вы хотите отменить рекламный пост и сделать возврат средств, то обратитесь к менеджеру - {manager_telegram}",
    "showall_empty": "Вы еще не создали ни одного поста для рекламы.",
}


text_message_photo = {
    "photo_uploaded": "Фото принято. Теперь отправьте текст для фото.",
    "photo_uploaded_as_file": "Фото принято как файл. Теперь отправьте текст для фото.",
    "edited_photo_verification":"Можете продолжить или повторить фото ещё раз.",
    "invalid_photo": "❌ Отправьте фото, а не текст.",
    "invalid_text": "Вы должны отправить Текст",
}

text_message_post_text = {
    "post_text_received": lambda post_text: f'Текст для поста: "{post_text}"\nПродолжим или хотите поменять текст на другой?',
}


text_message_payment = {
    "payment_invalid_photo": "Пожалуйста отправьте чек в виде PDF файла. Фото чека не подойдет.",
    "payment_invalid_rest": "Пожалуйста отправьте чек в виде PDF файла.",
    "payment_handle_pdf": "✅ Ваш чек был принят. Если вы ошиблись, можете поменять файл перед тем как он будет сохранен и отправлен на обработку менеджера.",
}





text_message_verification = {
    "confirm_photo_text__ask_post_text": "Отправьте текст для поста",
    
    "confirm_photo_text_no_post_text__ask_date": "Выберите дату публикации.",
    
    "confirm_post_text__ask_date": "Выберите дату публикации.",
    
    "confirm_selecting_date__ask_time": "Теперь выберите время публикации.",
    
    "confirm_selecting_time__final_verification": "Продолжим или если что-то хотите поменять начните заново",
    
    "confirm_selecting_time__show_post" : lambda post_text, formatted_date, post_time: (
        f"Текст под постом: '{post_text}'\nДата: {formatted_date}\nВремя: {post_time}"
        if post_text
        else f"Дата: {formatted_date}\nВремя: {post_time}"
    ),
    
    "confirm_final_verification__ask_pdf": f"Оплатите {price} через Kaspi номер: {kaspi_number}. После оплаты отправьте чек в виде PDF файла.",
    
    "confirm_payment__success": "Поздравляю, вы зарегистрировали новый пост для рекламы. В скором времени менеджер обработает вашу заявку!.",
    
    "retry_photo_text": "Пожалуйста отправьте фото заново",
    
    "retry_post_text": "Пожалуйста отправьте новый текст",
    
    "retry_selecting_date": "Выберите дату публикации.",
    
    "retry_selecting_time": "Выберите новое время публикации.",
    
    "retry_final_verification": "Отправьте, пожалуйста, новое фото для поста.",
    
    "retry_payment": "Отправьте пожалуйста новый чек.",
}


text_message_calendar = {
    "calendar_date_selected": lambda formatted_date: f'Вы выбрали {formatted_date}.\nВы можете поменять дату если ошиблись.',
}

text_message_time_picker = {
    "time_picker_time_selected": lambda chosen_hour: f"Выбранное время: {chosen_hour}. Если вы можете поменять время если ошиблись.",
}
