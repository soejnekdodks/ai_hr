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
        default="Qwen/Qwen3-0.6B",
        description="Базовая LLM модель"
    )
    LORA_MODEL: str = Field(
        default="antontuzov/liza-06-resume-russian",
        description="LoRA-адаптер для анализа резюме"
    )

    SEMANTIC_MODEL_NAME: str = Field(
        description="Модель для семантического сравнения",
        default="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    )

    LABELS: list[str] = Field(
        description="Типы сущностей",
        default=["SKILL", "EDUCATION", "EXPERIENCE", "PERSON", "LOCATION"]
    )

    DATASET_PATH: str = Field(
        description="Путь до датасета", default="./dataset/cv.json"
    )
    ENV: str = Field(description="Окружение: dev, prod", default="dev")


config = Config()
