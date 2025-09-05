import json
import os
import re
from typing import Dict, List

import torch
from config import config
from peft import PeftModel
from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoModelForTokenClassification,
    AutoTokenizer,
    pipeline,
)


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
    return task


class NERModel:
    def __init__(self, model_path=None):
        self.id_to_label = {i: label for i, label in enumerate(config.LABELS)}
        self.label_to_id = {label: i for i, label in enumerate(config.LABELS)}

        if model_path and os.path.exists(model_path):
            self.__load_model(model_path)
        else:
            self.__initialize_model()

    def __initialize_model(self):
        """Инициализация новой модели"""
        self.tokenizer = AutoTokenizer.from_pretrained(
            config.TOKEN_MODEL_NAME, add_prefix_space=True
        )

        # Конфигурация модели
        model_config = AutoConfig.from_pretrained(
            config.TOKEN_MODEL_NAME,
            num_labels=len(config.LABELS),
            id2label=self.id_to_label,
            label2id=self.label_to_id,
        )

        # Загрузка модели
        self.model = AutoModelForTokenClassification.from_pretrained(
            config.TOKEN_MODEL_NAME, config=model_config
        )

        # Создание pipeline для удобства
        self.pipeline = pipeline(
            "token-classification",
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy="simple",
        )

    def __load_model(self, model_path):
        """Загрузка сохраненной модели"""
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)

        model_config = AutoConfig.from_pretrained(
            model_path,
            num_labels=len(config.LABELS),
            id2label=self.id_to_label,
            label2id=self.label_to_id,
        )

        # 🔑 добавлен ignore_mismatched_sizes=True
        self.model = AutoModelForTokenClassification.from_pretrained(
            model_path, config=model_config, ignore_mismatched_sizes=True
        )

        self.pipeline = pipeline(
            "token-classification",
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy="simple",
        )


class ResumeParser:
    def __init__(self):
        # Загружаем базовую модель + LoRA
        base = AutoModelForCausalLM.from_pretrained(
            config.BASE_MODEL, torch_dtype=torch.float16, device_map="auto"
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
            prompt, return_tensors="pt", truncation=True, max_length=2048
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
            out[0][inputs.input_ids.shape[-1] :], skip_special_tokens=True
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
