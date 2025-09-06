import fitz  # PyMuPDF

def extract_text_from_pdf_pymupdf(pdf_path):
    """
    Извлекает текст из PDF с помощью PyMuPDF
    Быстрый и эффективный метод
    
    Args:
        pdf_path (str): Путь к PDF файлу
    
    Returns:
        str: Извлеченный текст
    """
    try:
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text() + "\n"
        
        return text
        
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return None

# Установка: pip install PyMuPDF