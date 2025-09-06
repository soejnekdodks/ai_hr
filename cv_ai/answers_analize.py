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


class AnswersAnalyzer:
    def __init__(self):
        self.model_manager = ModelManager()
        self.model, self.tokenizer, self.pipe = self.model_manager.get_model()

    def _run_model(self, prompt: str, max_new_tokens: int = 512) -> str:
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

    def analyze_answers(self, questions: list, answers: list) -> str:
        qa_text = "\n".join(
            [f"Вопрос: {q}\nОтвет: {a}" for q, a in zip(questions, answers)]
        )

        system_prompt = (
            "Ты — опытный интервьюер. Без комментариев и кратко оцени ответы кандидата на вопросы."
            "Дай числовую оценку от 0 до 100, где 0 — очень плохо, 100 — идеально. "
            "Составь очень краткий отчет в формате:\n"
            "Оценка: <число>\n"
            "Сильные стороны: ...\n"
            "Слабые стороны: ...\n"
            "Рекомендации: ..."
        )

        user_prompt = f"Вот список вопросов и ответов кандидата (ответы могут быть неразборчивы):\n\n{qa_text}"

        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        raw_output = self._run_model(full_prompt, max_new_tokens=256)

        return raw_output
