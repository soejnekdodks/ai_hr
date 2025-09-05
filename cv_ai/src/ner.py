import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from config import config


class ResumeVacancyAnalyze:
    def __init__(self, model_name: str = None, device_map="auto"):
        self.model_name = model_name or config.BASE_MODEL

        # Загружаем модель
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map=device_map,
            trust_remote_code=True,
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )

        # Настройка pad_token
        if self.tokenizer.pad_token_id is None:
            if self.tokenizer.eos_token_id is not None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            else:
                self.tokenizer.add_special_tokens({"pad_token": "[PAD]"})
                self.model.resize_token_embeddings(len(self.tokenizer))

    def _run_model(self, messages: list, max_new_tokens: int = 128) -> str:
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True).to(self.model.device)

        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.pad_token_id,
            )

        # Берем только сгенерированный ответ без промта
        text = self.tokenizer.decode(
            out[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True
        )
        return text.strip()

    def analyze_resume_vs_job(self, resume_text: str, vacancy_text: str) -> float:
        messages = [
            {"role": "system", "content": "Ты помощник, который анализирует резюме и вакансии. Ты можешь отвечать только одним числом от 0 до 100"},
            {"role": "user", "content": f"Проанализируй резюме и вакансию. Без лишних комментариев"
                                        f"Выпиши строго одно число - количество процентов того, каков шанс человеку пройти по данному резюме на данную вакансию.\n\nВакансия:\n{vacancy_text}\n\nРезюме:\n{resume_text}"}
        ]

        raw_output = self._run_model(messages)
        print("Модель ответила:", raw_output)

        numbers = re.findall(r"\d+(?:[\.,]\d+)?", raw_output)
        if numbers:
            try:
                num = float(numbers[0].replace(',', '.'))
                return min(max(num, 0.0), 100.0)
            except ValueError:
                pass

        return 0.0