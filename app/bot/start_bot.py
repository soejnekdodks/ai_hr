import asyncio

from aiogram import Bot, Dispatcher
from loguru import logger

from app.bot.analize import bot
from app.bot.handlers import router
from app.config import config

dp = Dispatcher()
dp.include_router(router)


async def start_bot():
    logger.info("Start polling")
    await dp.start_polling(bot)
    logger.info("Stop polling")
