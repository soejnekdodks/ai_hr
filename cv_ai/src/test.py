import re
from pprint import pprint

from api import cv_analize
from src.config import config

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
    text = re.sub(r"\"([А-Яа-яA-Za-z0-9\s\-]+)\"", r"«\1»", text)
    return text


with open(f"{config.PATH_TO_TEST_VACANCY}", "r", encoding="utf-8") as vaca:
    with open(f"{config.PATH_TO_TEST_RESUME}", "r", encoding="utf-8") as cv:
        resume_text = clean_quotes(cv.read())
        vacancy_text = clean_quotes(vaca.read())
        pprint(cv_analize(resume_text, vacancy_text))
