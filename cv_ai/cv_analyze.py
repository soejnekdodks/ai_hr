import re

import torch
from aiogram import Bot
from loguru import logger
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    pipeline,
)

from cv_ai.config import config
from cv_ai.model_init import ModelManager
from cv_ai.shrink import Shrinker


class ResumeVacancyAnalyze:
    def __init__(self):
        self.model_manager = ModelManager()
        self.model, self.tokenizer, self.pipe = self.model_manager.get_model()

    def _run_model(self, prompt: str, max_new_tokens: int = 10) -> str:
        try:
            formatted_prompt = self.tokenizer.apply_chat_template(
                [{"role": "user", "content": prompt}],
                tokenize=False,
                add_generation_prompt=True,
            )

            outputs = self.pipe(
                formatted_prompt,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                num_beams=1,
                temperature=0.0,
                top_k=50,
                top_p=0.95,
                eos_token_id=self.tokenizer.eos_token_id,
            )

            generated_text = outputs[0]["generated_text"][
                len(formatted_prompt) :
            ].strip()
            return generated_text

        except Exception as e:
            logger.info(f"Ошибка при генерации текста: {e}")
            return ""

    def analyze_resume_vs_vacancy(self, resume_text: str, vacancy_text: str) -> float:
        system_prompt = "Ты - эксперт по подбору персонала. Никакого дополнительного текста. Выводи только число от 0 до 100"

        user_prompt = (
            f"Оцени возможность кандидата пройти по данному резюме на работу по вакансии по шкале от 0 до 100, где 0 - полное несоответствие, 100 - идеальное соответствие.\n\n"
            f"ВАКАНСИЯ:\n{vacancy_text}\n\n"
            f"РЕЗЮМЕ:\n{resume_text}\n\n"
            f"Оценка соответствия (только число):"
        )

        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        raw_output = self._run_model(full_prompt, max_new_tokens=10)
        logger.info(f"Модель ответила: '{raw_output}'")
        
        # Ищем число в ответе
        match = re.search(r"(\d{1,3})", raw_output)
        if match:
            num = float(match.group(1))
            return max(0.0, min(100.0, num))
        else:
            logger.info(f"Не удалось извлечь число из ответа: '{raw_output}'")
            return -1

