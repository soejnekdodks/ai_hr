from sentence_transformers import SentenceTransformer, util
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from cv_ai.src.ner import NERModel

class EntityMatcher:
    def __init__(self):
        self.embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    def vectorize_entities(self, entities):
        """Создает векторное представление сущностей"""
        entity_texts = []
        entity_weights = []
        
        for entity in entities:
            entity_texts.append(entity['word'])
            entity_weights.append(entity['score'])  # Уверенность модели как вес
        
        # Эмбеддинги для всех сущностей
        embeddings = self.embedder.encode(entity_texts)
        
        return embeddings, entity_weights
    
    def calculate_similarity(self, embeddings1, embeddings2, weights1, weights2):
        """Вычисляет взвешенное косинусное сходство"""
        similarity_matrix = util.cos_sim(embeddings1, embeddings2)
        
        # Взвешенное среднее
        total_similarity = 0
        total_weight = 0
        
        for i in range(len(embeddings1)):
            for j in range(len(embeddings2)):
                similarity = similarity_matrix[i][j].item()
                weight = weights1[i] * weights2[j]  # Произведение весов
                total_similarity += similarity * weight
                total_weight += weight
        
        return total_similarity / total_weight if total_weight > 0 else 0


    def compare_by_category(self, resume_entities, vacancy_entities):
        """Сравнивает сущности по категориям"""
        category_scores = {}
        
        # Группируем сущности по категориям
        resume_by_category = {}
        vacancy_by_category = {}
        
        for entity in resume_entities:
            category = entity['entity_group']
            if category not in resume_by_category:
                resume_by_category[category] = []
            resume_by_category[category].append(entity)
        
        for entity in vacancy_entities:
            category = entity['entity_group']
            if category not in vacancy_by_category:
                vacancy_by_category[category] = []
            vacancy_by_category[category].append(entity)
        
        # Сравниваем каждую категорию
        for category in set(resume_by_category.keys()) | set(vacancy_by_category.keys()):
            resume_cat = resume_by_category.get(category, [])
            vacancy_cat = vacancy_by_category.get(category, [])
            
            if resume_cat and vacancy_cat:
                # Векторизуем сущности категории
                resume_emb, resume_weights = self.vectorize_entities(resume_cat)
                vacancy_emb, vacancy_weights = self.vectorize_entities(vacancy_cat)
                
                # Вычисляем сходство
                similarity = self.calculate_similarity(
                    resume_emb, vacancy_emb, resume_weights, vacancy_weights
                )
                category_scores[category] = similarity
        
        return category_scores

class ResumeVacancyMatcher:
    def __init__(self, model):
        # Загружаем NER модель
        self.ner_pipeline = model.pipeline

        # Загружаем модель для эмбеддингов
        self.embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # Веса для разных категорий
        self.category_weights = {
            "POSITION": 0.4,    # Должность - самый важный
            "SKILL": 0.3,       # Навыки
            "LOCATION": 0.15,   # Местоположение
            "COMPANY": 0.05,    # Компания
            "EDUCATION": 0.05,  # Образование
            "EXPERIENCE": 0.05  # Опыт
        }
    
    def match(self, resume_text, vacancy_text):
        """Сравнивает резюме и вакансию"""
        # Извлекаем сущности
        resume_entities = self.extract_entities(resume_text)
        vacancy_entities = self.extract_entities(vacancy_text)
        
        # Сравниваем по категориям
        category_scores = self.compare_by_category(resume_entities, vacancy_entities)
        
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
    
    def extract_entities(self, text):
        """Извлекает сущности из текста"""
        return self.ner_pipeline(text)
    
    def compare_by_category(self, resume_entities, vacancy_entities):
        """Сравнивает сущности по категориям"""
        category_scores = {}
        
        # Группируем по категориям
        resume_by_cat = self._group_by_category(resume_entities)
        vacancy_by_cat = self._group_by_category(vacancy_entities)
        
        # Сравниваем каждую категорию
        all_categories = set(resume_by_cat.keys()) | set(vacancy_by_cat.keys())
        
        for category in all_categories:
            resume_items = resume_by_cat.get(category, [])
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
    
    def _group_by_category(self, entities):
        """Группирует сущности по категориям"""
        grouped = {}
        for entity in entities:
            category = entity['entity_group']
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(entity)
        return grouped

# Инициализация
model = NERModel()

matcher = ResumeVacancyMatcher(model = model)

# Резюме и вакансия
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

# Сравнение
result = matcher.match(resume_text, vacancy_text)
def print_match_details(result):
    """Красивая печать результатов"""
    print("🎯 Match Results")
    print(f"Overall Score: {result['score']}%")
    print("\n📊 Category Scores:")
    for category, score in result['category_scores'].items():
        print(f"  {category:12}: {score:.3f}")
    
    print("\n📝 Resume Entities:")
    for entity in result['resume_entities']:
        print(f"  {entity['word']:15} → {entity['entity_group']}")
    
    print("\n📋 Vacancy Entities:")
    for entity in result['vacancy_entities']:
        print(f"  {entity['word']:15} → {entity['entity_group']}")

# Использование
print_match_details(result)



# import os 
# from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
# from transformers import AutoConfig
# from src.config import config

# class CVParserPipeline:
#     def __init__(self, config_path):
#         self.config = self.load_config(config_path)
#         self.initialize_components()
    
#     def initialize_components(self):
#         """Инициализация всех компонентов"""
#         self.data_loader = DataStreamer(
#             self.config['data_path'],
#             self.config['batch_size']
#         )
#         self.preprocessor = TextPreprocessor()
#         self.ner_model = NERModel(self.config['model_path'])
#         self.postprocessor = ResultPostprocessor()
#         self.cache = RedisCache() if self.config['use_cache'] else SimpleCache()
    
#     async def process_stream(self):
#         """Асинхронная обработка потока данных"""
#         async for batch in self.data_loader.async_stream():
#             processed_batch = await self.process_batch(batch)
#             yield processed_batch
    
#     async def process_batch(self, batch):
#         """Обработка батча данных"""
#         results = []
        
#         for cv_data in batch:
#             # Предобработка
#             normalized = self.preprocessor.normalize_cv(cv_data)
#             text = self.extract_text_for_ner(normalized)
            
#             # Кеширование
#             cache_key = self.generate_cache_key(text)
#             if cached := self.cache.get(cache_key):
#                 results.append(cached)
#                 continue
            
#             # NER обработка
#             entities = await self.ner_model.predict_async(text)
#             structured = self.postprocessor.structure_entities(entities, text)
            
#             # Сохранение в кеш
#             self.cache.set(cache_key, structured)
#             results.append(structured)
        
#         return results
    
#     def run(self):
#         """Запуск пайплайна"""
#         for batch in self.data_loader.stream_jsonl():
#             results = self.process_batch(batch)
#             self.save_results(results)
#             self.monitor.progress_update(len(results))


# from src.ner import NERModel
# from src.config import config

# def cv_analise(text: list[str]) -> None:
#     model = NERModel()
#     dct_out = {tag: "" for tag in config.LABELS}
#     for line in text:
#         results = model.pipeline(line)
#         for entity in results:
#             # TODO написать обработку, чтобы был словарь: ключи-теги, значения-списки слов
#             pass

