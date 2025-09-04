import re

import torch
from config import config
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


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

    def __build_prompt(self, text: str, mode: str = "resume") -> str:
        if mode == "resume":
            instruction = "Извлеките ключевые навыки, опыт и образование кандидата из текста резюме. Верните список. Без комментариев"
        else:
            instruction = "Извлеките ключевые требования и навыки из текста вакансии. Верните список. Без комментариев"
        return f"<|im_start|>user\n{instruction}\n\nТекст:\n{text}\n<|im_end|>\n<|im_start|>assistant\n"

    def extract_entities(self, text: str, mode: str = "resume") -> list[str]:
        """Возвращает список извлечённых скиллов/сущностей"""
        prompt = self.__build_prompt(text, mode)
        inputs = self.tokenizer(
            prompt, return_tensors="pt", truncation=True, max_length=2048
        ).to(self.model.device)

        with torch.no_grad():
            out = self.model.generate(**inputs, max_new_tokens=256, do_sample=False)

        result = self.tokenizer.decode(
            out[0][inputs.input_ids.shape[-1] :], skip_special_tokens=True
        )
        # Нормализуем список
        entities = [
            re.sub(r"[^а-яa-z0-9#+\-\. ]", "", x.strip().lower())
            for x in result.split("\n")
            if x.strip()
        ]
        entities = list(set([e for e in entities if len(e) > 1]))
        return entities
