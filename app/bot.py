import os
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command

# Создаем роутер для обработчиков
router = Router()

# Обработчики команд /start и /help
@router.message(Command("start", "help"))
async def cmd_start_help(message: Message):
    """
    Отправляет приветственное сообщение и объясняет принцип работы бота.
    """
    welcome_text = (
        "👋 Добро пожаловать в HR-бот для обработки вакансий и резюме!\n\n"
        "📋 **Принцип работы:**\n"
        "1. Загрузите файл с описанием вакансии в формате `.txt` или `.pdf`.\n"
        "2. Загрузите `.zip` архив, содержащий резюме кандидатов (файлы `.txt` или `.pdf` внутри).\n"
        "3. Бот проверит загрузку и сообщит, если чего-то не хватает.\n\n"
        "⚡ Просто отправьте файлы в нужных форматах, и бот сделает всё остальное!"
    )
    await message.answer(welcome_text)

# Обработчик для файлов с вакансиями
@router.message(F.document & (F.document.file_name.endswith('.txt') | F.document.file_name.endswith('.pdf')))
async def handle_vacancy_file(message: Message):
    """
    Обрабатывает загруженный файл вакансии (.txt или .pdf).
    Сохраняет информацию о загрузке в глобальную область видимости (в реальном проекте используйте БД!).
    """
    file_id = message.document.file_id
    file_name = message.document.file_name

    # Временное хранилище (в реальном проекте используйте БД или FSM)
    user_data = user_file_storage.get(message.from_user.id, {})
    user_data['vacancy_file'] = {'id': file_id, 'name': file_name}
    user_file_storage[message.from_user.id] = user_data

    await message.answer(f"✅ Вакансия `{file_name}` принята! Теперь загрузите ZIP-архив с резюме.")

# Обработчик для ZIP-архивов с резюме
@router.message(F.document & F.document.file_name.endswith('.zip'))
async def handle_resume_zip(message: Message):
    """
    Обрабатывает загруженный ZIP-архив с резюме.
    Проверяет, была ли загружена вакансия ранее.
    """
    user_id = message.from_user.id
    file_name = message.document.file_name

    # Проверяем, загружена ли вакансия
    user_data = user_file_storage.get(user_id, {})
    if 'vacancy_file' not in user_data:
        await message.answer("❌ Сначала загрузите файл с вакансией (.txt или .pdf)!")
        return

    # Сохраняем информацию об архиве
    user_data['resume_zip'] = {'id': message.document.file_id, 'name': file_name}
    user_file_storage[user_id] = user_data

    await message.answer(
        f"✅ Архив `{file_name}` с резюме принят!\n"
        f"💼 Вакансия: `{user_data['vacancy_file']['name']}`\n"
        "🎉 Все файлы получены. Обработка завершена!"
    )

# Обработчик для любых других документов (не тех, что нужны)
@router.message(F.document)
async def handle_unknown_document(message: Message):
    """Уведомляет пользователя о неверном формате файла."""
    file_name = message.document.file_name
    await message.answer(f"❌ Файл `{file_name}` не подходит. Нужен файл вакансии (.txt/.pdf) или ZIP-архив с резюме (.zip).")

# Обработчик для текстовых сообщений (игнорируем, но вежливо отвечаем)
@router.message(F.text)
async def handle_text(message: Message):
    """
    Игнорирует текстовые сообщения, но отправляет вежливый ответ,
    напоминая о необходимости загружать файлы.
    """
    await message.answer("📎 Я работаю только с файлами. Пожалуйста, загрузите файл вакансии (.txt или .pdf) или ZIP-архив с резюме.")

# Глобальный словарь для хранения данных пользователя (ВРЕМЕННОЕ РЕШЕНИЕ)
# В реальном проекте используйте базу данных или FSMContext!
user_file_storage = {}


import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Импортируем наш конфиг и роутеры из handlers

# Настраиваем логирование для отслеживания работы бота
logging.basicConfig(level=logging.INFO)

# Инициализируем хранилище для состояний FSM (пока используем память)
storage = MemoryStorage()

# Создаем объекты бота и диспетчера
bot = Bot(token="")
dp = Dispatcher(storage=storage)

# Подключаем роутер с обработчиками
dp.include_router(router)

async def main():
    """Основная функция для запуска поллинга бота."""
    logging.info("Бот запускается...")
    # Запускаем поллинг (опрос сервера Telegram на наличие новых апдейтов)
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Запускаем основную асинхронную функцию
    asyncio.run(main())
