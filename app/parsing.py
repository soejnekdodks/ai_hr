# app/utils/pdf_parser.py
import pdfplumber
import io
from fastapi import HTTPException

async def extract_text_from_pdf(pdf_file: UploadFile) -> str:
    """
    Извлекает текст из PDF файла.
    """
    try:
        # Читаем содержимое файла
        contents = await pdf_file.read()
        
        # Используем pdfplumber для извлечения текста
        text = ""
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="Не удалось извлечь текст из PDF файла")
        
        return text.strip()
    
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Ошибка при обработке PDF файла: {str(e)}"
        )