import zipfile
from io import BytesIO
from datetime import timedelta
import os

from aiogram import Router
from aiogram.types import Message, InputFile
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
import magic

from app.bot.start_bot import bot
from app.config import config
from app.database.core import get_async_session
from app.database.query.candidate import create as create_candidate
from app.database.query.interview import create as create_interview
from app.parsing import document_to_text
from cv_ai.cv_analyze import ResumeVacancyAnalyze
from cv_ai.questions_gen import QuestionsGenerator
from app.database.schema import Candidate

# Максимальные значения для проверки архива
MAX_ZIP_SIZE = 50 * 1024 * 1024  # 50MB
MAX_RESUMES_IN_ZIP = 10
MAX_RESUME_SIZE = 10 * 1024 * 1024  # 10MB

router = Router()

async def analyze_resume(
    message: Message,
    resume_bytes: bytes,
    vacancy_text: str,
    file_format: str,
    session: AsyncSession,
):
    """Анализ резюме и создание интервью (если прошло отбор)."""
    cv_analyze = ResumeVacancyAnalyze()
    resume_text = document_to_text(resume_bytes, file_format)

    match_percentage = cv_analyze.analyze_resume_vs_vacancy(resume_text, vacancy_text)
    url = create_mock()

    if match_percentage > 70.0:
        # --- Создаём кандидата ---
        candidate: Candidate = await create_candidate(session=session, cv=resume_bytes)

        # --- Генерируем вопросы ---
        qg = QuestionsGenerator()
        questions = qg.generate_questions(
            resume_text=resume_text,
            vacancy_text=vacancy_text,
            num_questions=config.NUMS_OF_QUESTIONS,
        )

        # --- Создаём интервью ---
        interview_id = await create_interview(
            session=session,
            candidate_id=candidate.id,
            questions=questions,
            expiration_time=timedelta(days=7),
        )

        # Получаем chat_id HR-у
        hr_chat_id = candidate.chat_id
        if not hr_chat_id:
            await message.answer("❌ Не удалось найти chat_id HR для кандидата.")
            return

        # --- Формируем сообщение HR ---
        file_info = get_file_info(resume_bytes, file_format)
        caption = (
            "🎯 Новый кандидат прошел первичный отбор!\n\n"
            f"🆔 ID кандидата: {candidate.id}\n"
            f"⚡️ Совпадение с вакансией: {match_percentage:.1f}%\n"
            f"📋 Интервью ID: {interview_id}\n"
            f"🔗 Ссылка на интервью: {url}"
        )

        cv_file = BytesIO(candidate.cv)
        filename = f"resume_candidate_{candidate.id}{file_info['extension']}"

        # Отправляем резюме HR-у
        await bot.send_document(
            chat_id=hr_chat_id,
            document=InputFile(cv_file, filename=filename),
            caption=caption,
        )
    else:
        await message.answer(
            f"❌ Резюме {file_format.upper()} не прошло отбор "
            f"(совпадение {match_percentage:.1f}%)."
        )


def get_file_info(file_bytes: bytes, original_format: str) -> dict:
    size_bytes = len(file_bytes)
    try:
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(file_bytes[:2048])
    except Exception:
        mime_type = f"application/{original_format}"

    mime_to_extension = {
        "application/pdf": ".pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "application/msword": ".doc",
        "text/plain": ".txt",
    }
    extension = mime_to_extension.get(mime_type, f".{original_format}")

    return {
        "size_bytes": size_bytes,
        "mime_type": mime_type,
        "format": original_format.upper(),
        "extension": extension,
    }