import zipfile
from io import BytesIO
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.analize import analyze_resume
from app.database.core import get_async_session
from app.parsing import document_to_text

router = Router()

# Константы ограничений
MAX_VACANCY_SIZE = 5 * 1024 * 1024  # 5MB
MAX_ZIP_SIZE = 10 * 1024 * 1024  # 10MB
MAX_RESUME_SIZE = 2 * 1024 * 1024  # 2MB
MAX_RESUMES_IN_ZIP = 10


@router.message(Command("start", "help"))
async def cmd_start_help(message: Message):
    welcome_text = (
        "👋 <b>Добро пожаловать в HR-бот для обработки вакансий и резюме!</b>\n\n"
        "📋 <b>Принцип работы:</b>\n"
        "1. Загрузите файл с описанием вакансии в формате <code>.txt</code> или <code>.pdf</code>\n"
        "2. Загрузите <code>.zip</code> архив, содержащий резюме кандидатов "
        "(файлы <code>.txt</code> или <code>.pdf</code> внутри)\n"
        "3. Бот проверит загрузку и сообщит, если чего-то не хватает\n\n"
        "⚡ <b>Ограничения:</b>\n"
        "• Вакансия: до 5MB\n"
        "• Архив: до 10MB\n"
        "• Резюме в архиве: до 2MB каждое\n"
        "• Максимум 10 резюме в архиве\n\n"
        "⚡ <i>Просто отправьте файлы в нужных форматах, и бот сделает всё остальное!</i>"
    )
    await message.answer(welcome_text, parse_mode="HTML")
@router.message(
    F.document
    & (F.document.file_name.endswith(".txt") | F.document.file_name.endswith(".pdf"))
)
async def handle_vacancy_file(message: Message):
    file_size = message.document.file_size

    if file_size > MAX_VACANCY_SIZE:
        await message.answer(
            f"❌ <b>Размер файла вакансии превышен!</b>\n\n"
            f"📊 <b>Текущий размер:</b> {file_size / 1024 / 1024:.1f}MB\n"
            f"📏 <b>Максимальный размер:</b> {MAX_VACANCY_SIZE / 1024 / 1024}MB\n\n"
            "📎 Пожалуйста, загрузите файл меньшего размера.",
            parse_mode="HTML",
        )
        return

    # Скачиваем файл
    try:
        file = await message.bot.get_file(message.document.file_id)
        downloaded = await message.bot.download_file(file.file_path)
        file_bytes = downloaded.read()
        
        file_name = message.document.file_name
        file_format = file_name.split(".")[-1].lower()

        user_data = user_file_storage.get(message.from_user.id, {})
        user_data["vacancy_file"] = {
            "id": message.document.file_id,
            "name": file_name,
            "size": file_size,
            "bytes": file_bytes,  # Сохраняем содержимое файла
            "format": file_format  # Сохраняем формат файла
        }
        user_file_storage[message.from_user.id] = user_data

        await message.answer(
            f"✅ <b>Вакансия</b> <code>{file_name}</code> <b>принята!</b>\n"
            f"📊 <b>Размер:</b> {file_size / 1024 / 1024:.1f}MB\n\n"
            "📦 Теперь загрузите ZIP-архив с резюме.",
            parse_mode="HTML",
        )
        
    except Exception as e:
        await message.answer(
            f"❌ <b>Ошибка при загрузке файла вакансии!</b>\n\n"
            f"<code>{str(e)}</code>",
            parse_mode="HTML",
        )


@router.message(F.document & F.document.file_name.endswith(".zip"))
async def handle_resume_zip(
    message: Message,
    session: AsyncSession = Depends(get_async_session),
):
    user_id = message.from_user.id
    file_name = message.document.file_name
    file_size = message.document.file_size

    # Проверка размера архива
    if file_size > MAX_ZIP_SIZE:
        await message.answer(
            f"❌ <b>Размер архива превышен!</b>\n\n"
            f"📊 <b>Текущий размер:</b> {file_size / 1024 / 1024:.1f}MB\n"
            f"📏 <b>Максимальный размер:</b> {MAX_ZIP_SIZE / 1024 / 1024}MB\n\n"
            "📎 Пожалуйста, загрузите архив меньшего размера.",
            parse_mode="HTML",
        )
        return

    user_data = user_file_storage.get(user_id, {})
    if "vacancy_file" not in user_data:
        await message.answer(
            "❌ <b>Сначала загрузите файл с вакансией!</b>\n",
            parse_mode="HTML",
        )
        return

    # Скачиваем и проверяем архив
    try:
        file = await message.bot.get_file(message.document.file_id)
        downloaded = await message.bot.download_file(file.file_path)

        with zipfile.ZipFile(BytesIO(downloaded.read())) as archive:
            resume_files = [
                name
                for name in archive.namelist()
                if name.lower().endswith((".pdf", ".txt", ".docx", ".doc"))
            ]

            if len(resume_files) > MAX_RESUMES_IN_ZIP:
                await message.answer(
                    f"❌ <b>Слишком много резюме в архиве!</b>\n\n"
                    f"📊 <b>Найдено резюме:</b> {len(resume_files)}\n"
                    f"📏 <b>Максимально разрешено:</b> {MAX_RESUMES_IN_ZIP}\n\n"
                    "📎 Пожалуйста, уменьшите количество резюме в архиве.",
                    parse_mode="HTML",
                )
                return

            # Проверяем размер каждого файла
            oversized_files = []
            for resume_name in resume_files:
                file_info = archive.getinfo(resume_name)
                if file_info.file_size > MAX_RESUME_SIZE:
                    oversized_files.append(
                        f"{resume_name} ({file_info.file_size / 1024 / 1024:.1f}MB)"
                    )

            if oversized_files:
                oversized_list = "\n".join([f"• {file}" for file in oversized_files])
                await message.answer(
                    f"❌ <b>Некоторые резюме превышают максимальный размер!</b>\n\n"
                    f"📏 <b>Максимальный размер резюме:</b> {MAX_RESUME_SIZE / 1024 / 1024}MB\n\n"
                    f"📎 <b>Файлы с превышением:</b>\n{oversized_list}\n\n"
                    "📎 Пожалуйста, уменьшите размер этих файлов и попробуйте снова.",
                    parse_mode="HTML",
                )
                return

            # --- Обработка нейросетью ---
            vacancy_file = user_data["vacancy_file"]
            vacancy_bytes = vacancy_file["bytes"]
            vacancy_format = vacancy_file["format"]
            vacancy_text = document_to_text(vacancy_bytes, vacancy_format)

            for resume_name in resume_files:
                resume_bytes = archive.read(resume_name)
                resume_format = resume_name.split(".")[-1].lower()

                await message.answer(f"резюме: {resume_bytes[:20]}\n\nвака: {c}")
                
                # Анализируем резюме
                await analyze_resume(
                    message=message,
                    resume_bytes=resume_bytes,
                    vacancy_text=vacancy_text,
                    file_format=resume_format,
                    session=session,
                )

    except zipfile.BadZipFile:
        await message.answer(
            "❌ <b>Некорректный ZIP-архив!</b>\n\n"
            "📎 Пожалуйста, убедитесь, что архив не поврежден и попробуйте снова.",
            parse_mode="HTML",
        )
        return
    except Exception as e:
        await message.answer(
            f"❌ <b>Ошибка при обработке архива!</b>\n\n"
            f"<code>{str(e)}</code>",
            parse_mode="HTML",
        )
        return

    user_data["resume_zip"] = {
        "id": message.document.file_id,
        "name": file_name,
        "size": file_size,
    }
    user_file_storage[user_id] = user_data

    await message.answer(
        f"✅ <b>Архив</b> <code>{file_name}</code> <b>с резюме принят и обработан!</b>",
        parse_mode="HTML",
    )

@router.message(F.document)
async def handle_unknown_document(message: Message):
    file_name = message.document.file_name
    await message.answer(
        f"❌ <b>Файл</b> <code>{file_name}</code> <b>не подходит</b>\n\n",
        parse_mode="HTML",
    )


@router.message(F.text)
async def handle_text(message: Message):
    await message.answer(
        "📎 <b>Я работаю только с файлами</b>\n\n"
        "📄 <b>Пожалуйста, загрузите:</b>\n"
        "• Файл вакансии\n"
        "• ZIP-архив с резюме (<code>.zip</code>)\n\n"
        "⚡ <b>Ограничения:</b>\n"
        "• Вакансия: до 5MB\n"
        "• Архив: до 10MB\n"
        "• Резюме в архиве: до 2MB каждое\n"
        "• Максимум 10 резюме в архиве",
        parse_mode="HTML",
    )


user_file_storage = {}
