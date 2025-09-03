import os 
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from transformers import AutoConfig
from src.config import config


class NERModel:
    def __init__(self, model_path=None):    
        self.id_to_label = {i: label for i, label in enumerate(config.LABELS)}
        self.label_to_id = {label: i for i, label in enumerate(config.LABELS)}
        
        if model_path and os.path.exists(model_path):
            self.__load_model(model_path)
        else:
            self.__initialize_model()

    def __initialize_model(self):
        """Инициализация новой модели"""
        self.tokenizer = AutoTokenizer.from_pretrained(
            config.TOKEN_MODEL_NAME,
            add_prefix_space=True
        )
        
        # Конфигурация модели
        model_config = AutoConfig.from_pretrained(
            config.TOKEN_MODEL_NAME,
            num_labels=len(config.LABELS),
            id2label=self.id_to_label,
            label2id=self.label_to_id
        )
        
        # Загрузка модели
        self.model = AutoModelForTokenClassification.from_pretrained(
            config.TOKEN_MODEL_NAME,
            config=model_config
        )
        
        # Создание pipeline для удобства
        self.pipeline = pipeline(
            "token-classification",
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy="simple"
        )
    
    def __load_model(self, model_path):
        """Загрузка сохраненной модели"""
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForTokenClassification.from_pretrained(model_path)
        self.pipeline = pipeline(
            "token-classification",
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy="simple"
        )
