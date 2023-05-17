import asyncio

from main import db, bot


async def notify_user(user_id, alert):
    await bot.send_message(user_id,f'✅Напоминаю вам о новой задаче!'
                                   f'\n'
                                   f'====ЗАДАЧА📋===='
                                   f'\n'
                                   f'{alert}')

    await db.del_task_user(user_id)

async def check_tasks():
    # Здесь происходит проверка задач в БД и уведомление пользователей
    while True:
        tasks = await db.get_all_user_alert()
        print(tasks)
        if tasks != None:
            for data in tasks:
                user_id = data[0]
                alert = data[1]
                await notify_user(user_id,alert)
        # Указываем периодичность проверки задач в секундах
        print('Проверяю !')
        await asyncio.sleep(60)  # Проверка каждую минуту