from sentence_transformers import SentenceTransformer, util
import sys
import os
from src.config import config
from src.ner import NERModel


class ResumeVacancyMatcher:
    def __init__(self, model):
        # Загружаем NER модель (сразу с aggregation_strategy)
        self.ner_pipeline = model.pipeline
        self.ner_pipeline = lambda text: model.pipeline(
            text,
            aggregation_strategy="simple"
        )

        self.embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        self.category_weights = {
            "LOCATION": 0.2,
            "EDUCATION": 0.4,
            "EXPERIENCE": 0.4,
        }

    def match(self, resume_text, vacancy_text):
        """Сравнивает резюме и вакансию"""
        # Извлекаем сущности
        resume_entities = self.__extract_entities(resume_text)
        vacancy_entities = self.__extract_entities(vacancy_text)
        
        # Сравниваем по категориям
        category_scores = self.__compare_by_category(resume_entities, vacancy_entities)
        
        # Общий score (взвешенная сумма)
        total_score = 0
        for category, score in category_scores.items():
            weight = self.category_weights.get(category, 0.01)
            total_score += score * weight
        
        # Нормализуем до 0-100
        final_score = min(100, max(0, total_score * 100))
        
        return {
            "score": round(final_score, 1),
            "category_scores": category_scores,
            "resume_entities": resume_entities,
            "vacancy_entities": vacancy_entities
        }
    
    def __extract_entities(self, text):
        raw_entities = self.ner_pipeline(text)
        return raw_entities
  
    def __compare_by_category(self, resume_entities, vacancy_entities):
        """Сравнивает сущности по категориям"""
        category_scores = {}
        
        # Группируем по категориям
        resume_by_cat = self.__group_by_category(resume_entities)
        vacancy_by_cat = self.__group_by_category(vacancy_entities)
        
        # Сравниваем каждую категорию
        all_categories = set(resume_by_cat.keys()) | set(vacancy_by_cat.keys())
        
        for category in all_categories:
            resume_items = vacancy_by_cat.get(category, [])
            vacancy_items = vacancy_by_cat.get(category, [])
            
            if resume_items and vacancy_items:
                # Векторизуем
                resume_emb = self.embedder.encode([e['word'] for e in resume_items])
                vacancy_emb = self.embedder.encode([e['word'] for e in vacancy_items])
                
                # Считаем сходство
                similarity = util.cos_sim(resume_emb, vacancy_emb).mean().item()
                category_scores[category] = similarity
            else:
                category_scores[category] = 0.0
        
        return category_scores
    
    def __group_by_category(self, entities):
        """Группирует сущности по категориям"""
        grouped = {}
        for entity in entities:
            category = entity['entity_group']
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(entity)
        return grouped

