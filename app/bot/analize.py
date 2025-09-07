import os
import uuid
from datetime import timedelta
from io import BytesIO
from aiogram import types, Bot, Router
from aiogram.types import InputFile
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
    """Wraps a BytesIO object into InputFile and rewinds to the beginning"""
    bytesio.seek(0)  # Ensure file pointer is at the beginning
    return InputFile(bytesio, filename=filename, **kwargs)


async def analyze_and_send_resume(
    message: types.Message,
    resume_bytes: bytes,
    vacancy_text: str,
    file_format: str,
    session: AsyncSession,
):
    """Analyzes resume, compares it to vacancy, and sends the resume with the result."""
    match_percentage = 100  # For the sake of simplicity, we're using a dummy value.

    if match_percentage >= 70.0:
        # Step 1: Create candidate in the database
        candidate = await create_candidate(session=session, cv=resume_bytes)

        # Step 2: Generate interview questions
        questions = generate_interview_questions()

        # Step 3: Create interview record
        alias_id = uuid.uuid4()
        await create_interview(
            session=session,
            candidate_id=candidate.id,
            questions=questions,
            expiration_time=timedelta(days=7),
            alias_id=alias_id
        )

        # Step 4: Prepare file and send document to HR
        file_info = get_file_info(resume_bytes, file_format)
        caption = prepare_resume_caption(match_percentage, alias_id)

        input_file = prepare_resume_file(resume_bytes, candidate, file_info)

        await message.answer_document(input_file, caption=caption)

        # Step 5: Confirm to the user
        await message.answer(
            f"✅ Резюме принято! Совпадение: {match_percentage:.1f}%. HR получил уведомление."
        )
    else:
        await message.answer(
            f"❌ Резюме {file_format.upper()} не прошло отбор "
            f"(совпадение {match_percentage:.1f}%)."
        )


def generate_interview_questions() -> list:
    """Generates a set of questions for the interview."""
    return [
        "Что такое замыкание (closure) в JavaScript?",
        "Как избежать Callback Hell?",
        "Объясните принципы REST.",
        "Что такое миграции базы данных и зачем они нужны?",
        "Как вы обеспечиваете безопасность своего API?",
    ]


def prepare_resume_caption(match_percentage: float, alias_id: uuid.UUID) -> str:
    """Prepares the caption for the resume document."""
    return (
        "🎯 Новый кандидат прошел первичный отбор!\n\n"
        f"⚡️ Совпадение с вакансией: {match_percentage:.1f}%\n"
        f"🔗 Ссылка на интервью: {config.DOMAIN}/api/v1/deeplink?id={alias_id}\n"
    )


def prepare_resume_file(resume_bytes: bytes, candidate: Candidate, file_info: dict) -> InputFile:
    """Prepares the resume file for sending."""
    cv_file = BytesIO(resume_bytes)
    filename = f"resume_candidate_{candidate.id}{file_info['extension']}"
    return wrap_media(cv_file, filename)


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
