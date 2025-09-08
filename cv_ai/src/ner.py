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

        if self.tokenizer.pad_token_id is None:
            if self.tokenizer.eos_token_id is not None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            else:
                self.tokenizer.add_special_tokens({"pad_token": "[PAD]"})
                self.model.resize_token_embeddings(len(self.tokenizer))

    def _run_model(self, prompt: str, max_new_tokens: int = 128) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True)
        device = next(self.model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            # Параметры генерации передаются напрямую в generate
            out = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,  # Параметры передаются напрямую
                temperature=0.0,
                top_p=0.95,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.pad_token_id,
            )
        text = self.tokenizer.decode(out[0], skip_special_tokens=True)
        return text

    def score_resume_vs_job(self, resume_text: str, vacancy_text: str) -> float:
        prompt = (
            "No eplanation and extra text!"
            "Vacancy:\n"
            f"{vacancy_text}\n\n"
            "Resume:\n"
            f"{resume_text}\n\n"
            "You are an strict hr assistant that compares a candidate resume and a job vacancy. "
            "Return a single number between 0 and 100 — the percent match (no explanation).\n"
            "Answer with a single number only."
        )

        raw_output = self._run_model(prompt) # Прогнали модель на промпте
        raw_output = self._run_model(prompt) # Она дала результат

        numbers = re.findall(r"\d+(?:[\.,]\d+)?", raw_output)
        if numbers:
            try:
                num = float(numbers[0].replace(',', '.'))
                return min(max(num, 0.0), 100.0)
            except ValueError:
                pass

        return 0.0