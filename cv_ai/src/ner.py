import os
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from transformers import AutoConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import json
import re
from typing import Dict, List
from config import config


def _build_json_instruction(mode: str) -> str:
    """Формирует инструкцию для модели."""
    if mode == "resume":
        task = (
            "Extract atomic data from the candidate's resume text. "
            "Fill in PERSON, CONTACT, BIRTHDATE, LOCATION, EDUCATION "
            "(UNIVERSITY, DEGREE, GRAD_YEAR), EXPERIENCE "
            "(COMPANY, POSITION, YEARS, ACHIEVEMENT), SKILL, TOOL, LANGUAGE, SOFT_SKILL."
        )
    else:
        task = (
            "Extract atomic requirements and conditions from the job description. "
            "Fill in REQUIREMENT, RESPONSIBILITY, CONDITION, SKILL, TOOL, LANGUAGE, "
            "SOFT_SKILL, and LOCATION."
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
=======
    labels_hint = ", ".join(config.LABELS)
    example = {k: [] for k in config.LABELS}

    return (
        f"{task}\n"
        f"Return STRICTLY valid JSON with this structure:\n"
        f"{json.dumps(example, ensure_ascii=False)}\n\n"
        f"Rules:\n"
        f"- JSON only, no comments or explanations.\n"
        f"- Each list item must be short and atomic.\n"
        f"- Do not invent data. If a section is empty, return [].\n"
        f"- Valid keys: {labels_hint}.\n"
    )


class ResumeParser:
    def __init__(self):
        # Загружаем модель
        self.model = AutoModelForCausalLM.from_pretrained(
            config.BASE_MODEL,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(config.BASE_MODEL)
        self.model.eval()

        # На всякий случай
        self.eos_token_id = getattr(self.tokenizer, "eos_token_id", None)

    def __build_prompt(self, text: str, mode: str) -> str:
        """Формирует ChatML-промпт."""
        instruction = _build_json_instruction(mode)
        return (
            f"<|im_start|>system\n{config.SYSTEM_PROMPT}<|im_end|>"
            f"<|im_start|>user\n{instruction}\n{text}<|im_end|>"
            f"<|im_start|>assistant\n"
        )

    def _run_model(self, prompt: str, max_new_tokens: int = 768) -> str:
        """Запуск генерации."""
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048
        ).to(self.model.device)

        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                temperature=0.0,
                eos_token_id=self.eos_token_id,
            )

        raw = self.tokenizer.decode(
            out[0][inputs.input_ids.shape[-1]:],
            skip_special_tokens=True
        )
        return raw.strip()

    @staticmethod
    def _json_only(s: str) -> Dict[str, List[str]]:
        """Попробовать распарсить JSON и нормализовать."""
        try:
            obj = json.loads(s)
        except Exception:
            return {k: [] for k in config.LABELS}

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
        """Нормализация строк."""
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

    def extract_entities(self, text: str, mode: str = "resume") -> dict:
        """Основной метод — получить JSON со структурой."""
        prompt = self.__build_prompt(text, mode)
        raw = self._run_model(prompt)

        # Иногда модель добавляет ```json блок
        raw = raw.replace("```json", "").replace("```", "").strip()

        data = self._json_only(raw)
        return {k: self._normalize(v) for k, v in data.items()}
