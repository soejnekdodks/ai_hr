import fitz


def pdf_to_text(pdf_path: str) -> str | None:
    try:
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text() + "\n"
        return text
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return None
