import torch
from config import config
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig

class AnswersAnalyzer:
    def __init__(self):
        self.model_name = config.BASE_MODEL

        # Если резко захотели ебнутый прирост производительности

        # bnb_config = BitsAndBytesConfig(
        #     load_in_4bit=True,
        #     bnb_4bit_compute_dtype=torch.bfloat16,  # можно заменить на torch.float16
        #     bnb_4bit_use_double_quant=True,
        #     bnb_4bit_quant_type="nf4"
        # )

        # quantization_config=bnb_config, # вместо torch_dtype

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="auto",              # сам распределит по GPU/CPU
            torch_dtype=torch.bfloat16,
            attn_implementation="sdpa",
            trust_remote_code=True
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer
        )

    def _run_model(self, prompt: str, max_new_tokens: int = 512) -> str:
        try:
            formatted_prompt = self.tokenizer.apply_chat_template(
                [{"role": "user", "content": prompt}],
                tokenize=False,
                add_generation_prompt=True
            )

            outputs = self.pipe(
                formatted_prompt,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                num_beams=1,
                temperature=0.6,
                top_k=50,
                top_p=0.95,
                eos_token_id=self.tokenizer.eos_token_id
            )

            generated_text = outputs[0]["generated_text"][len(formatted_prompt):].strip()
            return generated_text

        except Exception as e:
            print(f"Ошибка при генерации текста: {e}")
            return ""

    def analyze_answers(self, questions: list, answers: list) -> dict:
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

        return {raw_output}
