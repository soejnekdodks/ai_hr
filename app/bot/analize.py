import zipfile
from io import BytesIO
from datetime import timedelta

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


router = Router()


async def analyze_resume(
    message: Message,
    resume_bytes: bytes,
    vacancy_bytes: bytes,
    file_format: str,
    session: AsyncSession,
):
    """Анализ резюме и создание интервью (если прошло отбор)."""

    cv_analyze = ResumeVacancyAnalyze()
    resume_text = document_to_text(resume_bytes, file_format)
    vacancy_text = document_to_text(vacancy_bytes, file_format)

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

        await bot.send_document(
            chat_id=message.chat.id,
            document=InputFile(cv_file, filename=filename),
            caption=caption,
        )
    else:
        await message.answer(
            f"❌ Резюме {file_format.upper()} не прошло отбор "
            f"(совпадение {match_percentage:.1f}%)."
        )


# ---------------- Вспомогательные функции ----------------

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


def create_mock() -> str:
    """Временная заглушка для генерации ссылки на интервью."""
    return "https://example.com/interview/mock"
