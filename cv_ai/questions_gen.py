import torch
from cv_ai.config import config
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    pipeline,
)


class QuestionsGenerator:
    def __init__(self):
        self.model_name = config.BASE_MODEL

        # bnb_config = BitsAndBytesConfig(
        #     load_in_4bit=True,
        #     bnb_4bit_compute_dtype=torch.bfloat16,  # можно заменить на torch.float16
        #     bnb_4bit_use_double_quant=True,
        #     bnb_4bit_quant_type="nf4"
        # )

        # quantization_config=bnb_config, # вместо torch_dtype

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="auto",  # сам распределит по GPU/CPU
            torch_dtype=torch.bfloat16,
            attn_implementation="sdpa",
            trust_remote_code=True,
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, trust_remote_code=True
        )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.pipe = pipeline(
            "text-generation", model=self.model, tokenizer=self.tokenizer
        )

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
                do_sample=True,
                num_beams=1,
                temperature=0.7,
                top_k=50,
                top_p=0.95,
                eos_token_id=self.tokenizer.eos_token_id,
            )

            generated_text = outputs[0]["generated_text"][
                len(formatted_prompt) :
            ].strip()
            return generated_text

        except Exception as e:
            print(f"Ошибка при генерации текста: {e}")
            return ""

    def generate_questions(
        self, resume_text: str, vacancy_text: str, num_questions: int = 8
    ) -> list:
        system_prompt = (
            "Ты — опытный HR-интервьюер. Не пиши лишние комментарии. Твоя задача — придумать конкретные и осмысленные вопросы для интервью, "
            "исходя из требований вакансии и опыта кандидата. "
        )

        user_prompt = (
            f"Составь список из {num_questions} коротких вопросов для собеседования.\n"
            f"Основывайся на резюме и вакансии.\n\n"
            f"ВАКАНСИЯ:\n{vacancy_text}\n\n"
            f"РЕЗЮМЕ:\n{resume_text}\n\n"
            f"Вопросы:"
        )

        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        raw_output = self._run_model(full_prompt, max_new_tokens=256)

        # Разбиваем результат построчно и убираем пустые строки
        questions = [q.strip("- ") for q in raw_output.split("\n") if q.strip()]

        return questions[:num_questions]
