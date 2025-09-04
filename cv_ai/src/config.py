from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    # Базовая модель + адаптер
    BASE_MODEL: str = Field(
        default="Qwen/Qwen1.5-4B-Chat",
        description="Базовая LLM модель"
    )

    # Модель эмбеддингов для семантического сравнения
    # Можно заменить на 'intfloat/multilingual-e5-large' при наличии кода пула,
    # но для совместимости оставляем Sentence-Transformers модель.
    SEMANTIC_MODEL_NAME: str = Field(
        description="Модель для семантического сравнения",
        default="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    )

    # Порог совпадения скиллов в косинусной близости [0..1]
    MATCH_THRESHOLD: float = Field(
        default=0.78,
        description="Порог для мэчинга скиллов по эмбеддингам"
    )

    # Какие лейблы участвуют в метриках совпадения (по умолчанию только SKILL)
    METRIC_LABELS: list[str] = Field(
        default=["SKILL"],
        description="Список лейблов, по которым считаем метрики"
    )

    # Системный промпт и формат ответа
    SYSTEM_PROMPT: str = Field(
        default=(
            "You must always respond ONLY with valid JSON object."
            "Do not repeat input text. Do not output explanations."
            "If unsure — return empty lists."
        ),
        description="Системные инструкции для модели"
    )


    LABELS: list[str] = [
        "SKILL", "SOFT_SKILL", "TOOL", "LANGUAGE",
        "EDUCATION", "DEGREE", "UNIVERSITY", "GRAD_YEAR",
        "EXPERIENCE", "COMPANY", "POSITION", "YEARS", "ACHIEVEMENT",
        "PERSON", "LOCATION", "CONTACT", "BIRTHDATE",
        "RESPONSIBILITY", "REQUIREMENT", "CONDITION"
    ]

    # 2) По каким меткам считаем метрики (по умолчанию как было):
    METRIC_LABELS: list[str] = ["SKILL"]  # при желании добавьте "REQUIREMENT", и т.п.

    # 3) Схема: добавили properties и убрали required
    JSON_SCHEMA: dict = {
        "type": "object",
        "properties": {
            "SKILL": {"type": "array", "items": {"type": "string"}},
            "SOFT_SKILL": {"type": "array", "items": {"type": "string"}},
            "TOOL": {"type": "array", "items": {"type": "string"}},
            "LANGUAGE": {"type": "array", "items": {"type": "string"}},

            "EDUCATION": {"type": "array", "items": {"type": "string"}},
            "DEGREE": {"type": "array", "items": {"type": "string"}},
            "UNIVERSITY": {"type": "array", "items": {"type": "string"}},
            "GRAD_YEAR": {"type": "array", "items": {"type": "string"}},

            "EXPERIENCE": {"type": "array", "items": {"type": "string"}},
            "COMPANY": {"type": "array", "items": {"type": "string"}},
            "POSITION": {"type": "array", "items": {"type": "string"}},
            "YEARS": {"type": "array", "items": {"type": "string"}},
            "ACHIEVEMENT": {"type": "array", "items": {"type": "string"}},

            "PERSON": {"type": "array", "items": {"type": "string"}},
            "LOCATION": {"type": "array", "items": {"type": "string"}},
            "CONTACT": {"type": "array", "items": {"type": "string"}},
            "BIRTHDATE": {"type": "array", "items": {"type": "string"}},

            "RESPONSIBILITY": {"type": "array", "items": {"type": "string"}},
            "REQUIREMENT": {"type": "array", "items": {"type": "string"}},
            "CONDITION": {"type": "array", "items": {"type": "string"}}
        },
        "additionalProperties": False
    }

    DATASET_PATH: str = Field(
        description="Путь до датасета", default="./dataset/cv.json"
    )
    ENV: str = Field(description="Окружение: dev, prod", default="dev")
    PATH_TO_TEST_VACANCY: str = Field(description="Путь до тестовой вакансии", default="/Users/brmstr/Repos/ai_hr/ai_hr/cv_ai/src/dataset/вакансия.txt")
    PATH_TO_TEST_RESUME: str = Field(description="Путь до тестового резюме", default="/Users/brmstr/Repos/ai_hr/ai_hr/cv_ai/src/dataset/резюме.txt")


config = Config()