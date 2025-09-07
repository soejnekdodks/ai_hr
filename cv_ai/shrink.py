import torch
from loguru import logger
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    pipeline,
)

from cv_ai.config import config
from cv_ai.model_init import ModelManager


class Shrinker:
    def __init__(self):
        self.model_manager = ModelManager()
        self.model, self.tokenizer, self.pipe = self.model_manager.get_model()

    def _run_model(self, prompt: str, max_new_tokens: int = 256) -> str:
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

    def resume_shrink(self, resume_text: str) -> list:
        system_prompt = (
            """
            Анализируй предоставленное резюме как Senior HR-специалист. Сделай сжатый структурированный анализ по шаблону:

            1. **Кандидат** - [Должность, уровень, общий стаж]
            2. **Ключевая экспертиза** - [Ядерные компетенции и специализация]
            3. **Карьерный путь** - [Ключевые компании и позиции, рост]
            4. **Tech Stack** - [Технологии и инструменты, уровень владения]
            5. **Достижения** - [3-5 конкретных измеримых результатов]
            6. **Fit** - [Гибрид/офис, релокация, ожидания по ЗП]

            Сохрани профессиональный HR-язык. Избегай общих фраз. Сфокусируйся на измеримых результатах и релевантном опыте.
            """
        )

        user_prompt = (
            f"РЕЗЮМЕ:\n{resume_text}\n\n"
        )

        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        raw_output = self._run_model(full_prompt, max_new_tokens=512)

        return raw_output
    
    def vacancy_shrink(self, vacancy_text: str) -> list:
        system_prompt = (
            """
            Анализируй текст вакансии ниже как Senior HR-специалист. Сделай сжатый структурированный анализ по шаблону:

            1. **Позиция** - [Название должности]
            2. **Суть роли** - [1-2 предложения о главной цели роли]
            3. **Key Responsibilities** - [ключевые задачи]
            4. **Must-Have Hard Skills** - [Критичные технические навыки]
            5. **Soft Skills & Fit** - [Ключевые личные качества и fit с культурой]
            6. **Условия** - [Формат работы, вилка оплаты, бенефиты]

            Сохрани профессиональный HR-язык. Избегай воды. Сфокусируйся на фактах из вакансии.
            """
        )

        user_prompt = (
            f"ВАКАНСИЯ:\n{vacancy_text}\n\n"
        )

        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        raw_output = self._run_model(full_prompt, max_new_tokens=512)

        return raw_output

