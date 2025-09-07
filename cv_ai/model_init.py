from cv_ai.config import config
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    pipeline,
)
from loguru import logger
import os


class ModelManager:
    _instance = None
    _model_initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._model_initialized:
            self.model_name = config.BASE_MODEL
            self.cache_dir = "./model_cache"
            self.model = None
            self.tokenizer = None
            self.pipe = None
            self._model_initialized = True
            os.makedirs(self.cache_dir, exist_ok=True)
            logger.info(f"Кэш моделей: {os.path.abspath(self.cache_dir)}")

    def initialize_model(self):
        if self.model is not None:
            return self.model, self.tokenizer, self.pipe

        logger.info(f"Загрузка модели {self.model_name} с 4-бит квантованием...")

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )

        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map="auto",
                torch_dtype=torch.bfloat16,
                low_cpu_mem_usage=True,
                trust_remote_code=True,
                cache_dir=self.cache_dir,
                quantization_config=bnb_config,
            )
            self.model = torch.compile(self.model)  # 🔥 Оптимизация PyTorch 2.0+

            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                cache_dir=self.cache_dir,
                use_fast=True,  # 🔥 быстрее
            )

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.pipe = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device_map="auto",
            )

            logger.info("Модель загружена, скомпилирована и готова к работе.")
        except Exception as e:
            logger.error(f"Ошибка при загрузке модели: {e}")
            raise

        return self.model, self.tokenizer, self.pipe

    def get_model(self):
        if self.model is None:
            return self.initialize_model()
        return self.model, self.tokenizer, self.pipe

    def clear_cache(self):
        self.model = None
        self.tokenizer = None
        self.pipe = None
        logger.info("Кэш модели очищен")
