import re
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext

import config
from handlers import db
from keyboards.user_keyboard import cb, start_keyboard, cb_del, delete_task, cancel_keyboard
from main import dp

#Обработчик прекращения записи
from misc.time_user import get_time_user
from states.state_user import AlertState


@dp.callback_query_handler(cb.filter(action='cancel'),state='*')
async def cancel_alert(call:types.CallbackQuery,state:FSMContext):
    await call.answer()
    await call.message.answer('Запись сброшена👌🏻.',reply_markup=start_keyboard())
    await call.message.delete()
    await state.reset_state()

#Обработчик выборочного удаления задачи
@dp.callback_query_handler(cb_del.filter(action='deleted'),state='*')
async def deleted_notify(call:types.CallbackQuery,callback_data:dict):
    await call.answer()
    await db.del_task(callback_data.get('task'))
    await call.message.answer('Задача удалена')
    await call.message.delete()


#Обработчик изменения времени записи (из main удалил db)
@dp.callback_query_handler(cb_del.filter(action='change_time'),state='*')
async def change_time(call:types.CallbackQuery,callback_data:dict,state:FSMContext):
    await call.answer()
    async with state.proxy() as data:
        data['alert_change'] = callback_data.get('task')
    await call.message.answer('Введите новове время для задачи',reply_markup=cancel_keyboard())
    await AlertState.change_time.set()


@dp.message_handler(state=AlertState.change_time)
async def save_change_time(message:types.Message,state:FSMContext):
    msg = message.text
    # Вывод в формате МЕСЯЦ.ДЕНЬ ЧАСЫ:МИНУТЫ
    if not re.match(r'[\d]{1,2}\.[\d]{1,2} [\d]{1,2}:[\d]{1,2}', msg):  # 12.05 00:55
        await message.answer(config.WTIME_WRONG, reply_markup=cancel_keyboard())
    else:
        # Получаем текущий год
        current_year = datetime.now().year
        # Парсим текст на (месяц число часы минуты)
        user_time = get_time_user(message.text)
        # Создаем обьект даты и времени пользователя
        date_time_user = datetime(year=current_year,
                                  month=int(user_time[1]),
                                  day=int(user_time[0]),
                                  hour=int(user_time[2]),
                                  minute=int(user_time[3]),
                                  second=00)
        # Проверка на время
        if date_time_user < datetime.now():
            await message.answer('Кажется вы записали неправильно время или дату🧐.', reply_markup=cancel_keyboard())
        else:
            async with state.proxy() as data:
                alert = data.get('alert_change')
                await db.change_time(date_time_user,message.from_user.id,alert)
            await message.answer('Ваша задача сохранена!\n'
                                 f'📋Задача:{alert}\n'
                                 f'===⏱Время: {date_time_user}===', reply_markup=delete_task(alert))
            await state.finish() #

#Изменение задачи
@dp.callback_query_handler(cb_del.filter(action='change_alert'),state='*')
async def change_alert(call:types.CallbackQuery,callback_data:dict,state:FSMContext):
    await call.answer()
    async with state.proxy() as data:
        data['change_alert'] = callback_data.get('task')
    await call.message.answer('Что вы хотите подправить в задаче?')
    await call.message.delete()
    await AlertState.change_alert.set()


@dp.message_handler(state=AlertState.change_alert)
async def save_change_alert(message:types.Message,state:FSMContext):
    async with state.proxy() as data:
        alert = data.get('change_alert')
    time = await db.get_time(message.from_user.id,alert)
    await db.change_alert(message.text,message.from_user.id,time)
    await message.answer('Задача отредактирована')
    await state.finish()