from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("start", "help"))
async def cmd_start_help(message: Message):
    welcome_text = (
        "👋 <b>Добро пожаловать в HR-бот для обработки вакансий и резюме!</b>\n\n"
        "📋 <b>Принцип работы:</b>\n"
        "1. Загрузите файл с описанием вакансии в формате <code>.txt</code> или <code>.pdf</code>\n"
        "2. Загрузите <code>.zip</code> архив, содержащий резюме кандидатов "
        "(файлы <code>.txt</code> или <code>.pdf</code> внутри)\n"
        "3. Бот проверит загрузку и сообщит, если чего-то не хватает\n\n"
        "⚡ <i>Просто отправьте файлы в нужных форматах, и бот сделает всё остальное!</i>"
    )
    await message.answer(welcome_text, parse_mode="HTML")


@router.message(
    F.document
    & (F.document.file_name.endswith(".txt") | F.document.file_name.endswith(".pdf"))
)
async def handle_vacancy_file(message: Message):
    file_id = message.document.file_id
    file_name = message.document.file_name

    user_data = user_file_storage.get(message.from_user.id, {})
    user_data["vacancy_file"] = {"id": file_id, "name": file_name}
    user_file_storage[message.from_user.id] = user_data

    await message.answer(
        f"✅ <b>Вакансия</b> <code>{file_name}</code> <b>принята!</b>\n\n"
        "📦 Теперь загрузите ZIP-архив с резюме.",
        parse_mode="HTML",
    )


@router.message(F.document & F.document.file_name.endswith(".zip"))
async def handle_resume_zip(message: Message):
    user_id = message.from_user.id
    file_name = message.document.file_name

    user_data = user_file_storage.get(user_id, {})
    if "vacancy_file" not in user_data:
        await message.answer(
            "❌ <b>Сначала загрузите файл с вакансией!</b>\n"
            "📄 Форматы: <code>.txt</code> или <code>.pdf</code>",
            parse_mode="HTML",
        )
        return

    user_data["resume_zip"] = {"id": message.document.file_id, "name": file_name}
    user_file_storage[user_id] = user_data

    await message.answer(
        f"✅ <b>Архив</b> <code>{file_name}</code> <b>с резюме принят!</b>\n"
        f"💼 <b>Вакансия:</b> <code>{user_data['vacancy_file']['name']}</code>\n\n"
        "🎉 <b>Все файлы получены. Обработка завершена!</b>",
        parse_mode="HTML",
    )


@router.message(F.document)
async def handle_unknown_document(message: Message):
    file_name = message.document.file_name
    await message.answer(
        f"❌ <b>Файл</b> <code>{file_name}</code> <b>не подходит</b>\n\n"
        "📎 <b>Нужно отправить:</b>\n"
        "• Файл вакансии: <code>.txt</code> или <code>.pdf</code>\n"
        "• ZIP-архив с резюме: <code>.zip</code>",
        parse_mode="HTML",
    )


@router.message(F.text)
async def handle_text(message: Message):
    await message.answer(
        "📎 <b>Я работаю только с файлами</b>\n\n"
        "📄 <b>Пожалуйста, загрузите:</b>\n"
        "• Файл вакансии (<code>.txt</code> или <code>.pdf</code>)\n"
        "• ZIP-архив с резюме (<code>.zip</code>)",
        parse_mode="HTML",
    )


user_file_storage = {}
