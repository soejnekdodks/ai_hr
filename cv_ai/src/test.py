from src.api import cv_analize
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

pprint(cv_analize(resume_text, vacancy_text))


# with open("/Users/brmstr/Repos/ai_hr/ai_hr/cv_ai/src/dataset/вакансия.txt", "r") as vaca:
#     with open("/Users/brmstr/Repos/ai_hr/ai_hr/cv_ai/src/dataset/резюме.txt", "r") as cv:
#         pprint(cv_analize(cv.read(), vaca.read()))
