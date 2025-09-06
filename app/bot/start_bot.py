import asyncio

from aiogram import Bot, Dispatcher
from loguru import logger

from app.bot.handlers import router
from app.config import config

bot = Bot(config.TG_TOKEN)
dp = Dispatcher()
dp.include_router(router)


def start_bot():
    logger.info("Start polling")
    asyncio.run(dp.start_polling(bot))
    logger.info("Stop polling")
