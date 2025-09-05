import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from config import config
from peft import PeftModel
from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoModelForTokenClassification,
    AutoTokenizer,
    pipeline,
)



<<<<<<< HEAD

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
=======
class ResumeVacancyAnalyze:
    def __init__(self, model_name: str = None, device_map="auto"):
        self.model_name = model_name or config.BASE_MODEL

        # Загружаем модель
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map=device_map,
            trust_remote_code=True,
>>>>>>> app_branch
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

<<<<<<< HEAD
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
=======
    def _run_model(self, prompt: str, max_new_tokens: int = 128) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True)
        device = next(self.model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
>>>>>>> app_branch

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

<<<<<<< HEAD
        raw = self.tokenizer.decode(
            out[0][inputs.input_ids.shape[-1] :], skip_special_tokens=True
=======
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
>>>>>>> app_branch
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