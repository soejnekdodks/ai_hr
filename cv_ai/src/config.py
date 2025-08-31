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
    MODEL_NAME: str = Field(
        description="Название модели", default="cointegrated/rubert-tiny2"
    )
    TAGS: list[str] = Field(
        description="Список тегов для определения",
        default=["O", "SKILL", "EXPERIENCE", "EDUCATION"],
    )
    DATASET_PATH: str = Field(
        description="Путь до датасета", default="./dataset/cv.json"
    )


config = Config()
