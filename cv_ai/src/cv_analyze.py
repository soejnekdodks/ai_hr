import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig

class ResumeVacancyAnalyze:
    def __init__(self, model_name: str = "Vikhrmodels/Vikhr-7B-instruct_0.4"):
        self.model_name = model_name
        
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,  # можно заменить на torch.float16
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="cuda",              # сам распределит по GPU/CPU
            quantization_config=bnb_config, # вместо torch_dtype
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

    def _run_model(self, prompt: str, max_new_tokens: int = 10) -> str:
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
                temperature=0.1,
                top_k=50,
                top_p=0.98,
                eos_token_id=self.tokenizer.eos_token_id
            )
            
            generated_text = outputs[0]['generated_text'][len(formatted_prompt):].strip()
            return generated_text
            
        except Exception as e:
            print(f"Ошибка при генерации текста: {e}")
            return ""

    def analyze_resume_vs_vacancy(self, resume_text: str, vacancy_text: str) -> float:
        system_prompt = "Ты - эксперт по подбору персонала. Никакого дополнительного текста. Выводи только число от 0 до 100"
        
        user_prompt = (
            f"Оцени возможность кандидата пройти по данному резюме на работу по вакансии по шкале от 0 до 100, где 0 - полное несоответствие, 100 - идеальное соответствие.\n\n"
            f"ВАКАНСИЯ:\n{vacancy_text}\n\n"
            f"РЕЗЮМЕ:\n{resume_text}\n\n"
            f"Оценка соответствия (только число):"
        )
        
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        try:
            raw_output = self._run_model(full_prompt, max_new_tokens=10)
            print(f"Модель ответила: '{raw_output}'")
            
            # Ищем число в ответе
            match = re.search(r"(\d{1,3})", raw_output)
            if match:
                num = float(match.group(1))
                return max(0.0, min(100.0, num))
            else:
                print(f"Не удалось извлечь число из ответа: '{raw_output}'")
                return 0.0
                
        except Exception as e:
            print(f"Ошибка при анализе соответствия: {e}")
            return 0.0