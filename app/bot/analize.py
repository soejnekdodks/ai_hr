import os
import uuid
from datetime import timedelta
from io import BytesIO
from aiogram import types, Bot, Router
from aiogram.types import BufferedInputFile, FSInputFile  # Измененный импорт
from fastapi import Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import config
from app.database.core import get_async_session
from app.database.query.candidate import create as create_candidate
from app.database.query.interview import create as create_interview
from app.database.schema import Candidate
from app.parsing import document_to_text
from cv_ai.cv_analyze import ResumeVacancyAnalyze
from cv_ai.questions_gen import QuestionsGenerator
from cv_ai.shrink import Shrinker

# Максимальные значения для проверки архива
MAX_ZIP_SIZE = 50 * 1024 * 1024  # 50MB
MAX_RESUMES_IN_ZIP = 10
MAX_RESUME_SIZE = 10 * 1024 * 1024  # 10MB

router = Router()
bot = Bot(config.TG_TOKEN)

def wrap_media(bytesio, filename, **kwargs):
    bytesio.seek(0)
    return BufferedInputFile(
        file=bytesio.getvalue(),  
        filename=filename,
        **kwargs
    )

def prepare_resume_file(resume_bytes: bytes, candidate: Candidate, file_info: dict) -> BufferedInputFile:

    filename = f"resume_candidate_{candidate.id}{file_info['extension']}"
    
    return BufferedInputFile(
        file=resume_bytes,
        filename=filename
    )

async def analyze_resume(
    message: types.Message,
    resume_bytes: bytes,
    vacancy_text: str,
    file_format: str,
    session: AsyncSession,
):
    shrinker = Shrinker()

    resume = document_to_text(resume_bytes, file_format)

    resume = shrinker.resume_shrink(resume)
    vacancy_text = shrinker.vacancy_shrink(vacancy_text)

    cv_analyze = ResumeVacancyAnalyze()

    match_percentage = cv_analyze.analyze_resume_vs_vacancy(resume, vacancy_text)

    if match_percentage >= 70.0:
        candidate = await create_candidate(session=session, cv=resume_bytes, chat_id = str(message.chat.id))

        qg = QuestionsGenerator()
        questions = qg.generate_questions(vacancy_text, resume, config.NUMS_OF_QUESTIONS)

        alias_id = uuid.uuid4()

        await create_interview(
            session=session,
            candidate_id=candidate.id,
            questions=questions,
            expiration_time=timedelta(days=7),
            alias_id=alias_id
        )

        file_info = get_file_info(resume_bytes, file_format)
        caption = prepare_resume_caption(match_percentage, alias_id, candidate_id=candidate.id)

        input_file = prepare_resume_file(resume_bytes, candidate, file_info)

        await message.answer_document(input_file, caption=caption)

        await message.answer(
            f"✅ Резюме принято! Совпадение: {match_percentage:.1f}%. HR получил уведомление."
        )
    else:
        await message.answer(
            f"❌ Резюме {file_format.upper()} не прошло отбор "
            f"(совпадение {match_percentage:.1f}%)."
        )


def prepare_resume_caption(match_percentage: float, alias_id: uuid.UUID, candidate_id: int) -> str:
    """Prepares the caption for the resume document."""
    return (
        "🎯 Новый кандидат прошел первичный отбор!\n\n"
        f"ID кандидата: {candidate_id}\n"
        f"⚡️ Совпадение с вакансией: {match_percentage:.1f}%\n"
        f"🔗 Ссылка на интервью: {config.DOMAIN}/api/v1/deeplink?id={alias_id}\n"
    )


def get_file_info(file_bytes: bytes, original_format: str) -> dict:
    """Returns file information such as size, MIME type, format, and extension."""
    size_bytes = len(file_bytes)
    mime_type, extension = detect_file_type(file_bytes)
    
    if mime_type == "application/octet-stream":
        mime_type = f"application/{original_format}"
        extension = f".{original_format}"

    return {
        "size_bytes": size_bytes,
        "mime_type": mime_type,
        "format": original_format.upper(),
        "extension": extension,
    }


def detect_file_type(file_bytes: bytes) -> tuple:
    """Detects the MIME type and extension of the file based on its signature."""
    if len(file_bytes) < 4:
        return "application/octet-stream", ".bin"
    
    if file_bytes.startswith(b'%PDF-'):
        return "application/pdf", ".pdf"
    
    if file_bytes.startswith(b'PK'):
        return "application/zip", ".zip"
    
    if file_bytes.startswith(b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'):
        return "application/msword", ".doc"
    
    if file_bytes.startswith(b'{\\rtf'):
        return "application/rtf", ".rtf"
    
    if file_bytes.startswith(b'\xEF\xBB\xBF'):
        return "text/plain", ".txt"
    
    if file_bytes.startswith(b'<!DOCTYPE') or file_bytes.startswith(b'<html'):
        return "text/html", ".html"
    
    return "application/octet-stream", ".bin"


def format_file_size(size_bytes: int) -> str:
    """Formats file size into a readable string (e.g., 10.5 MB)."""
    size_names = ["B", "KB", "MB", "GB"]
    size = size_bytes
    i = 0
    while size >= 1024 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    return f"{size:.1f} {size_names[i]}"
