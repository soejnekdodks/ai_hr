import os

import torch
from loguru import logger
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    pipeline,
)

from cv_ai.config import config


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

        logger.info(f"Загрузка модели {self.model_name} без 4-бит квантизации...")

        try:
            # Выбираем dtype в зависимости от доступности GPU
            torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map="auto" if torch.cuda.is_available() else None,
                torch_dtype=torch_dtype,
                low_cpu_mem_usage=True,
                trust_remote_code=True,
                cache_dir=self.cache_dir,
            )

            # Оптимизация PyTorch 2.0+ (если доступно)
            try:
                self.model = torch.compile(self.model)
            except Exception as compile_err:
                logger.warning(f"torch.compile не поддерживается: {compile_err}")

            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                cache_dir=self.cache_dir,
                use_fast=True,
            )

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.pipe = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device_map="auto" if torch.cuda.is_available() else None,
            )

            logger.info("Модель загружена и готова к работе (FP16/FP32).")
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
