import asyncio

from aiogram import Bot,Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

import config
from middlewares.middleware import ThrottlingMiddleware
from services.sql import DataBase

db = DataBase(config.DATABASE)

storage = MemoryStorage()
bot = Bot(config.BOT_TOKEN,parse_mode='HTML')
dp = Dispatcher(bot,storage=storage)


async def on_startup(_):
    await bot.send_message(config.ADMINS,'Запуск бота')



if __name__=='__main__':
    from handlers import dp
    from services.send_notify import check_tasks

    dp.middleware.setup(ThrottlingMiddleware())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(check_tasks())
    executor.start_polling(dispatcher=dp,skip_updates=True,on_startup=on_startup)