from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    # Базовая модель DeepSeek (Hugging Face)
    BASE_MODEL: str = Field(
        default="Qwen/Qwen1.5-4B-Chat",
        description="Базовая модель для DeepSeek"
    )
    # Путь до датасета (пример)
    PATH_TO_DATASET: str = Field(
        description="Путь до датасета",
        default="./dataset/cv.json"
    )
    ENV: str = Field(description="Окружение: dev, prod", default="dev")

    PATH_TO_TEST_VACANCY: str = Field(
        description="Путь до тестовой вакансии",
        default="dataset/вакансия.txt"
    )
    PATH_TO_TEST_RESUME: str = Field(
        description="Путь до тестового резюме",
        default="dataset/резюме.txt"
    )

config = Config()