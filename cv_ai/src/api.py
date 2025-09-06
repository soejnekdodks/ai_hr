from src.main_pipeline import ResumeVacancyMatcher
from src.ner import NERModel #"/Users/brmstr/Repos/ai_hr/ai_hr/cv_ai/src/ner_model/"
from src.ner2 import ContextualNER
from src.config import config


def cv_analize(resume_text: str, vacancy_text: str) -> dict:
    model = NERModel("/Users/brmstr/Repos/ai_hr/ai_hr/cv_ai/src/ner_model/")
    matcher = ResumeVacancyMatcher(model=model)
    result = matcher.match(resume_text, vacancy_text)
    data = {}
    data["score"] = result['score']
    data['category_scores'] = {}
    for category, score in result['category_scores'].items():
        data['category_scores'][category] = float(score)

    if config.ENV == "dev":
        data['resume_entities'] = {}
        for entity in result['resume_entities']:
            data['resume_entities'][entity['word']] = entity

        data['vacancy_entities'] = {}
        for entity in result['vacancy_entities']:
            data['vacancy_entities'][entity['word']] = entity

    return data
