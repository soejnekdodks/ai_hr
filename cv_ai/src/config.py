from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )
    MODEL_PATH: str = Field(
        description="Дирректория с дообученной моделью", default="./cv_model"
    )
    TOKEN_MODEL_NAME: str = Field(
        description="Название модели для выделениея токенов", default="cointegrated/rubert-tiny2"
    )
    SEMANTIC_MODEL_NAME: str = Field(
        description="Название модели для семантического анализа", default="paraphrase-multilingual-MiniLM-L12-v2"
    )
    LABELS: list[str] = Field(
        description="Список тегов для определения",
        default=[
            "O", "B-PERSON", "I-PERSON", "B-LOCATION", "I-LOCATION",
            "B-POSITION", "I-POSITION", "B-SKILL", "I-SKILL", "B-COMPANY", "I-COMPANY",
            "B-EMAIL", "I-EMAIL", "B-PHONE", "I-PHONE"
        ],
    )
    DATASET_PATH: str = Field(
        description="Путь до датасета", default="./dataset/cv.json"
    )


config = Config()
