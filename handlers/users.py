import asyncio
import logging
import re
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

import config
from main import dp
from services.sql import DataBase
from keyboards.user_keyboard import start_keyboard, cancel_keyboard, cb, delete_task, cb_del
from states.state_user import AlertState
from misc.time_user import get_time_user
from middlewares.middleware import rate_limit

db = DataBase(config.DATABASE)

@rate_limit(5)
@dp.message_handler(Command('start'))
async def start_user_cmnd(message:types.Message):
    if await db.user_exist(message.from_user.id): #Если он есть в базе данных
        await message.answer(config.START_TEXT,reply_markup=start_keyboard()) #reply_markup - Начать запись
    else:
        try:
            await db.add_user(message.from_user.id, message.from_user.first_name)
        except Exception as e:
            logging.info(f'Ошибка при добавлениее в базу данных юзера {e}')
        finally:
            await message.answer(config.START_TEXT, reply_markup=start_keyboard())



#Нажатие на кнопку 'Начать запись'
@dp.message_handler(text='📝Записать задачу',content_types='text')
async def start_task(message:types.Message):
    await message.answer(config.ALERT_TEXT,reply_markup=cancel_keyboard())
    await AlertState.alert.set()



#Любой контект тайпс , фото тоже (добавить позже)
@dp.message_handler(state=AlertState.alert,content_types=types.ContentTypes.ANY)
async def save_alert(message:types.Message,state:FSMContext):
    if message.content_type != types.ContentType.TEXT:
        await message.answer('Введите текст.')
    else:
        async with state.proxy() as data:
            data['alert'] = message.text
        await message.answer(config.WTIME_TEXT,reply_markup=cancel_keyboard())

        await AlertState.time.set()




#Сохранение времени
@dp.message_handler(content_types=types.ContentType.TEXT,state=AlertState.time)
async def save_time(message:types.Message,state:FSMContext):
    msg = message.text
    #Вывод в формате МЕСЯЦ.ДЕНЬ ЧАСЫ:МИНУТЫ
    if not re.match(r'[\d]{1,2}\.[\d]{1,2} [\d]{1,2}:[\d]{1,2}',msg):
        await message.answer(config.WTIME_WRONG,reply_markup=cancel_keyboard())
    else:
        # Получаем текущий год
        current_year = datetime.now().year
        #Парсим текст на (месяц число часы минуты)
        user_time = get_time_user(message.text)
        #Создаем обьект даты и времени пользователя
        date_time_user = datetime(year=current_year,
                                      month=int(user_time[1]),
                                      day=int(user_time[0]),
                                      hour=int(user_time[2]),
                                      minute=int(user_time[3]),
                                      second=00)
        #Проверка на время
        if date_time_user < datetime.now():
            await message.answer(config.WTIME_OLD,reply_markup=cancel_keyboard())
        else:
            async with state.proxy() as data:
                await db.add_new_task(message.from_user.id,data.get('alert'),date_time_user)
            await message.answer('<b>Ваша задача успешно сохранена!</b>'
                                 '\n'
                                 f'====⏱Время: {date_time_user}===='
                                 f'\n'
                                 f'📋Задача: {data.get("alert")}',reply_markup=delete_task(data.get('alert')))
            await state.finish()


@dp.message_handler(text='⭕Удалить все задачи')
async def del_tasks(message:types.Message):
    await db.del_task_user(message.from_user.id)
    await message.answer('👨‍💻Задачи успешно удалены!')



#Мои задачи
@dp.message_handler(text='📁Мои задачи')
async def my_tasks(message:types.Message):
    data_task = await db.get_all_notify(message.from_user.id)
    if data_task:
        for data in data_task:
            alert = data[0]
            time = data[1]
            await message.answer(f'📊<b>Вот твои задачи</b>'
                                 f'\n'
                                 f'====ВРЕМЯ🕘===='
                                 f'\n'
                                 f'{time}'
                                 f'\n'
                                 f'====ЗАДАЧА📋===='
                                 f'\n'
                                 f'{alert}',reply_markup=delete_task(alert))
    else:
        await message.answer(config.MY_TASKS_NO,reply_markup=start_keyboard())

@rate_limit(5)
@dp.message_handler()
async def other_cmnd(message:types.Message):
    await message.answer('Я вас не понимаю')




