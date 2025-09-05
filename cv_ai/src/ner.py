import torch
import re
from transformers import AutoTokenizer, AutoModelForCausalLM
from config import config

class ResumeParser:
    def __init__(self):
        # Загрузка модели и токенизатора для DeepSeek-V2-Lite
        self.model = AutoModelForCausalLM.from_pretrained(
            config.BASE_MODEL,
            dtype=torch.float16,  # Новый синтаксис вместо torch_dtype
            device_map="auto",    # Автораспределение по GPU
        )
        self.tokenizer = AutoTokenizer.from_pretrained(config.BASE_MODEL)

        # Фикс пад-токена
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model.eval()
        self.eos_token_id = getattr(self.tokenizer, "eos_token_id", None)

    def __build_prompt(self, text: str) -> str:
        # Стандартный текстовый prompt для модели
        return f"{config.SYSTEM_PROMPT}\n\n{text}"

    def _run_model(self, prompt: str, max_new_tokens: int = 64) -> str:
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=1024
        ).to(self.model.device)

        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,  # Отключаем случайность для предсказуемости
                top_p=1.0,        # Используем максимальный срез вероятностей
                top_k=50,         # Устанавливаем top-k для предотвращения повторений
                no_repeat_ngram_size=3,  # Запрещаем повторение n-грамм (увеличено до 3)
                pad_token_id=self.tokenizer.eos_token_id  # Устанавливаем пад-токен
            )

        # Декодируем только сгенерированный текст
        decoded = self.tokenizer.decode(
            out[0][inputs.input_ids.shape[-1]:],
            skip_special_tokens=True
        )
        return decoded.strip()

    def evaluate_match(self, resume_text: str, vacancy_text: str) -> float:
        prompt = (
            f"Вакансия:\n{vacancy_text}\n\n"
            f"Резюме:\n{resume_text}\n\n"
        )

        for attempt in range(3):
            full_prompt = self.__build_prompt(prompt)
            raw_output = self._run_model(full_prompt, max_new_tokens=64)
            print(raw_output)
            # Извлекаем числа из текста
            numbers = re.findall(r"\d+(?:\.\d+)?", raw_output)
            if numbers:
                try:
                    # Возвращаем минимальное значение (чтобы избежать ошибок на невалидных данных)
                    match_percentage = float(numbers[0])
                    # Ограничиваем результат 100
                    return min(100.0, match_percentage)
                except ValueError:
                    continue
        # fallback: если нет валидных чисел, возвращаем 0
        return 0.0