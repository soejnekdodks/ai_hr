from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch
import json
import re
from typing import Dict, List
from config import config

def _build_json_instruction(mode: str) -> str:
    if mode == "resume":
        task = (
            "Извлеките из текста резюме кандидата атомарные данные. "
            "Заполните ФИО (PERSON), контакты (CONTACT, BIRTHDATE, LOCATION), "
            "образование (UNIVERSITY, DEGREE, GRAD_YEAR, EDUCATION), "
            "опыт работы (COMPANY, POSITION, YEARS, EXPERIENCE, ACHIEVEMENT), "
            "навыки (SKILL, TOOL, LANGUAGE, SOFT_SKILL)."
        )
    else:
        task = (
            "Извлеките из текста вакансии атомарные требования и условия. "
            "Заполните требования (REQUIREMENT), обязанности (RESPONSIBILITY), "
            "условия (CONDITION), технические навыки (SKILL, TOOL, LANGUAGE), "
            "soft skills (SOFT_SKILL), локацию (LOCATION)."
        )

    labels_hint = ", ".join(config.LABELS)
    example = {
        "SKILL": [],
        "EDUCATION": [],
        "EXPERIENCE": [],
        "PERSON": [],
        "LOCATION": [],
        "SOFT_SKILL": []
    }
    
    return (
        f"{task}. Верните СТРОГО валидный JSON со структурами:\n"
        f"{json.dumps(example, ensure_ascii=False)}\n"
        f"Требования:\n"
        f"— Только JSON, без комментариев и объяснений.\n"
        f"— Каждый элемент списка должен быть коротким и атомарным.\n"
        f"— Не придумывайте данные. Если раздел пуст, верните пустой список.\n"
        f"— Допустимые ключи: {labels_hint}.\n"
    )

class ResumeParser:
    def __init__(self):
        # Загружаем базовую модель + LoRA
        base = AutoModelForCausalLM.from_pretrained(
            config.BASE_MODEL,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        tokenizer = AutoTokenizer.from_pretrained(config.BASE_MODEL)
        self.model = PeftModel.from_pretrained(base, config.LORA_MODEL)
        self.tokenizer = tokenizer
        self.model.eval()

        # В некоторых сборках Qwen3 нет eos_token_id — защитимся
        self.eos_token_id = getattr(self.tokenizer, "eos_token_id", None)

    def __build_prompt(self, text: str, mode: str = "resume") -> str:
        # Используем рекомендованный на странице модели ChatML-формат
        # и явно запрещаем размышления / chain-of-thought.
        instruction = _build_json_instruction(mode)
        return (
            f"<|im_start|>system{config.SYSTEM_PROMPT}<|im_end|>"
            f"<|im_start|>user{instruction}Текст:{text}<|im_end|>"
            f"<|im_start|>assistant"
        )

    @staticmethod
    def _json_only(s: str) -> Dict[str, List[str]]:
        def _default():
            return {k: [] for k in config.LABELS}

        try:
            obj = json.loads(s)
        except Exception:
            # fallback — ищем первый большой блок {...}
            matches = re.findall(r"\{.*\}", s, flags=re.DOTALL)
            if not matches:
                return _default()
            for frag in matches:
                try:
                    obj = json.loads(frag)
                    break
                except Exception:
                    continue
            else:
                return _default()

        result = {}
        for k in config.LABELS:
            val = obj.get(k, [])
            if isinstance(val, str):
                result[k] = [val]
            elif isinstance(val, list):
                result[k] = [str(x) for x in val if isinstance(x, (str, int, float))]
            else:
                result[k] = []
        return result
        
    @staticmethod
    def _normalize(items: List[str]) -> List[str]:
        out = []
        for x in items:
            x = str(x).strip().lower()
            x = re.sub(r"[^a-zа-яё0-9@+/#.\- ,;:()]+", "", x, flags=re.IGNORECASE)
            x = re.sub(r"\s+", " ", x)
            if len(x) > 1:
                out.append(x)
        seen, uniq = set(), []
        for x in out:
            if x not in seen:
                uniq.append(x)
                seen.add(x)
        return uniq
        
    def _run_model(self, prompt: str) -> str:
        """Запускает модель и возвращает сырой текст (без постобработки)."""
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048
        ).to(self.model.device)

        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                max_new_tokens=384,
                do_sample=False,  # детерминированный вывод
                temperature=0.0,
                eos_token_id=self.eos_token_id,
            )

        raw = self.tokenizer.decode(
            out[0][inputs.input_ids.shape[-1]:],
            skip_special_tokens=True
        )
        return raw

    def extract_entities(self, text: str, mode: str = "resume") -> dict:
        """
        Возвращает dict с ключами из config.LABELS.
        Двухшаговый подход:
        1. Прогрев — модель думает, но выводит только 'OK'.
        2. Основной шаг — модель выдаёт чистый JSON.
        """

        # 1. Прогрев
        warmup_prompt = (
            f"<|im_start|>system{config.SYSTEM_PROMPT}<|im_end|>"
            f"<|im_start|>Сначала проанализируй текст и подумай, какие данные нужно извлечь. "
            f"Выведи только 'OK'. Текст: {text}<|im_end|>"
            f"<|im_start|>assistant"
        )
        _ = self._run_model(warmup_prompt)

        # 2. Основной вызов
        prompt = self.__build_prompt(text, mode)
        raw = self._run_model(prompt)

        raw = raw.lstrip(" :\n\t")
        raw = raw.replace("```json", "").replace("```", "")
        raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

        print(raw)

        data = self._json_only(raw)
        return {k: self._normalize(v) for k, v in data.items()}