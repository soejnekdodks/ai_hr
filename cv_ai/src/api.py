from main_pipeline import ResumeVacancyMatcher
from config import config


def cv_analize(resume_text: str, vacancy_text: str) -> dict:
    matcher = ResumeVacancyMatcher()
    result = matcher.match(resume_text, vacancy_text)

    data = {
        # убираем несуществующий "similarity"
        "precision": result["precision"],
        "recall": result["recall"],
        "f1": result["f1"],
    }

    if config.ENV == "dev":
        # правильные ключи — "resume" и "vacancy"
        data["resume_entities"] = result["resume"]
        data["vacancy_entities"] = result["vacancy"]

    return data
