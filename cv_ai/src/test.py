import re
from api import cv_analize
from pprint import pprint

resume_text = """
Иванов Иван Python разработчик с 5 летним опытом.
Работал в Яндексе с Django и Flask. 
Проживает в Москве. Высшее образование МГУ.
"""

vacancy_text = """
Ищем Senior Python developer с опытом работы от 3 лет.
Требования: Django, Flask, PostgreSQL. 
Работа в Москве. Офис в центре города.
"""

# pprint(cv_analize(resume_text, vacancy_text))

def clean_quotes(text: str) -> str:
    # заменяем "..." внутри русских слов на «...»
    text = re.sub(r'\"([А-Яа-яA-Za-z0-9\s\-]+)\"', r'«\1»', text)
    return text



with open("C:\\Users\\user\source\\repos\\ai_hr\\ai_hr\cv_ai\src\dataset\вакансия.txt", "r", encoding="utf-8") as vaca:
    with open("C:\\Users\\user\source\\repos\\ai_hr\\ai_hr\cv_ai\src\dataset\резюме.txt", "r", encoding="utf-8") as cv:
        resume_text = clean_quotes(cv.read())
        vacancy_text = clean_quotes(vaca.read())
        pprint(cv_analize(resume_text, vacancy_text))
