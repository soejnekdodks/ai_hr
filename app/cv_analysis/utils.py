import pdfplumber
from docx import Document
import os

def extract_text_from_pdf(file_path: str) -> str:
    """Извлечение текста из PDF"""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise Exception(f"Ошибка чтения PDF: {str(e)}")
    return text.strip()

def extract_text_from_docx(file_path: str) -> str:
    """Извлечение текста из DOCX"""
    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
        return text.strip()
    except Exception as e:
        raise Exception(f"Ошибка чтения DOCX: {str(e)}")

def extract_text_from_txt(file_path: str) -> str:
    """Извлечение текста из TXT"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            return text.strip()
    except Exception as e:
        raise Exception(f"Ошибка чтения TXT: {str(e)}")

def extract_text(file_path: str) -> str:
    """Извлечение текста из файла"""
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    elif file_path.endswith('.txt'):
        return extract_text_from_txt(file_path)
    else:
        raise ValueError("Unsupported file format. Supported: PDF, DOCX, TXT")