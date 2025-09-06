import zipfile
from io import BytesIO
from datetime import timedelta
import os

from aiogram import Router
from aiogram.types import Message, InputFile
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

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

from aiogram import Bot
bot = Bot(config.TG_TOKEN)

def create_mock():
    """Заглушка для создания mock URL"""
    return "https://example.com/interview/mock-id"

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

        # Получаем chat_id HR-а
        hr_chat_id = message.chat.id
        
        # --- Формируем сообщение HR ---
        file_info = get_file_info(resume_bytes, file_format)
        caption = (
            "🎯 Новый кандидат прошел первичный отбор!\n\n"
            f"🆔 ID кандидата: {candidate.id}\n"
            f"⚡️ Совпадение с вакансией: {match_percentage:.1f}%\n"
            f"📋 Интервью ID: {interview_id}\n"
            f"🔗 Ссылка на интервью: {url}\n"
            f"📄 Формат: {file_info['format']}\n"
            f"📏 Размер: {format_file_size(file_info['size_bytes'])}"
        )

        cv_file = BytesIO(candidate.cv)
        filename = f"resume_candidate_{candidate.id}{file_info['extension']}"

        # Отправляем резюме HR-у
        await bot.send_document(
            chat_id=hr_chat_id,
            document=InputFile(cv_file, filename=filename),
            caption=caption,
        )
        
        # Подтверждение пользователю
        await message.answer(
            f"✅ Резюме принято! Совпадение: {match_percentage:.1f}%. "
            f"HR получил уведомление."
        )
    else:
        await message.answer(
            f"❌ Резюме {file_format.upper()} не прошло отбор "
            f"(совпадение {match_percentage:.1f}%)."
        )


def get_file_info(file_bytes: bytes, original_format: str) -> dict:
    """Определяет информацию о файле по сигнатурам"""
    size_bytes = len(file_bytes)
    
    # Определяем MIME-type по сигнатурам файлов
    mime_type, extension = detect_file_type(file_bytes)
    
    # Если не удалось определить, используем оригинальный формат
    if mime_type == "application/octet-stream":
        mime_type = f"application/{original_format}"
        extension = f".{original_format}"

    return {
        "size_bytes": size_bytes,
        "mime_type": mime_type,
        "format": original_format.upper(),
        "extension": extension,
    }


def detect_file_type(file_bytes: bytes) -> tuple[str, str]:
    """Определяет тип файла по сигнатурам"""
    if len(file_bytes) < 4:
        return "application/octet-stream", ".bin"
    
    # PDF: %PDF-
    if file_bytes.startswith(b'%PDF-'):
        return "application/pdf", ".pdf"
    
    # ZIP-based formats (DOCX, XLSX, PPTX, etc.)
    if file_bytes.startswith(b'PK'):
        return "application/zip", ".zip"
    
    # Microsoft DOC (OLE Compound Document)
    if file_bytes.startswith(b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'):
        return "application/msword", ".doc"
    
    # RTF: {\rtf
    if file_bytes.startswith(b'{\\rtf'):
        return "application/rtf", ".rtf"
    
    # Plain text (UTF-8 BOM)
    if file_bytes.startswith(b'\xEF\xBB\xBF'):
        return "text/plain", ".txt"
    
    # Plain text (UTF-16)
    if file_bytes.startswith(b'\xFF\xFE') or file_bytes.startswith(b'\xFE\xFF'):
        return "text/plain", ".txt"
    
    # HTML
    if file_bytes.startswith(b'<!DOCTYPE') or file_bytes.startswith(b'<html'):
        return "text/html", ".html"
    
    # RAR
    if file_bytes.startswith(b'Rar!'):
        return "application/vnd.rar", ".rar"
    
    # 7ZIP
    if file_bytes.startswith(b'7z'):
        return "application/x-7z-compressed", ".7z"
    
    # По умолчанию
    return "application/octet-stream", ".bin"


def format_file_size(size_bytes: int) -> str:
    """Конвертирует размер в байтах в читаемый формат"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    size = size_bytes
    while size >= 1024 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


# Дополнительная функция для определения расширения по оригинальному формату
def get_extension_by_format(file_format: str) -> str:
    """Возвращает расширение файла на основе формата"""
    extensions = {
        'pdf': '.pdf',
        'docx': '.docx',
        'doc': '.doc',
        'txt': '.txt',
        'rtf': '.rtf',
        'html': '.html',
        'zip': '.zip',
        'rar': '.rar',
    }
    return extensions.get(file_format.lower(), f'.{file_format}')