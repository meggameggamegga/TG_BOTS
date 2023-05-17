from aiogram.types import ReplyKeyboardMarkup,KeyboardButton,InlineKeyboardButton,InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData


def start_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True,row_width=3,one_time_keyboard=True)
    keyboard.insert(KeyboardButton(text='📝Записать задачу'))
    keyboard.add(KeyboardButton(text='📁Мои задачи'))
    keyboard.add(KeyboardButton(text='⭕Удалить все задачи'))
    return keyboard

cb = CallbackData('btn','action')

def cancel_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Завершить запись',callback_data=cb.new(action='cancel')))
    return keyboard

cb_del = CallbackData('btn','action','task')

def delete_task(task):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Удалить задачу', callback_data=cb_del.new(action='deleted',task=task)))
    keyboard.add(InlineKeyboardButton(text='Изменить время',callback_data=cb_del.new(action='change_time',task=task)))
    keyboard.add(InlineKeyboardButton(text='Изменить задачу',callback_data=cb_del.new(action='change_alert',task=task)))
    print(task)
    return keyboard