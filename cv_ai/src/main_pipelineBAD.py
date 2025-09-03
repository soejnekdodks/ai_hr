from sentence_transformers import SentenceTransformer, util
from sklearn.metrics import precision_score, recall_score, f1_score
import numpy as np

from ner2 import ResumeParser
from config import config


class ResumeVacancyMatcher:
    def __init__(self):
        self.parser = ResumeParser()
        self.embedder = SentenceTransformer(config.SEMANTIC_MODEL_NAME)

    def match(self, resume_text: str, vacancy_text: str) -> dict:
        # Извлечение сущностей
        resume_entities = self.parser.extract_entities(resume_text, mode="resume")
        vacancy_entities = self.parser.extract_entities(vacancy_text, mode="vacancy")

        # Семантическое сходство (общий текст)
        emb_resume = self.embedder.encode(resume_text, convert_to_tensor=True)
        emb_vacancy = self.embedder.encode(vacancy_text, convert_to_tensor=True)
        similarity = util.cos_sim(emb_resume, emb_vacancy).item()

        # Метрики пересечения навыков (по ключам)
        y_true = [1] * len(vacancy_entities)
        y_pred = [1 if v in resume_entities else 0 for v in vacancy_entities]

        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)

        return {
            "similarity": round(similarity, 3),
            "precision": round(float(precision), 3),
            "recall": round(float(recall), 3),
            "f1": round(float(f1), 3),
            "resume_entities": resume_entities,
            "vacancy_entities": vacancy_entities,
        }
