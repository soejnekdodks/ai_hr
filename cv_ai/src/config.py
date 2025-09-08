from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    # Заменяем на DeepSeek-V2-Lite модель с Hugging Face
    BASE_MODEL: str = Field(
        default="deepseek-ai/DeepSeek-V2-Lite",  # Указываем модель DeepSeek
        description="Базовая модель для DeepSeek"
    )

    SYSTEM_PROMPT: str = Field(
        default=(
            "Сравни вакансию и резюме и дай только одно число, которое будет означать процент соответствия между ними. "
            "Это число должно быть в пределах от 0 до 100. "
            "Не выводи никаких дополнительных символов, текста или описаний, только число. "
            "Пример правильного вывода: 85. "
            "Никаких других фраз или списков не должно быть."
        ),
        description="Системные инструкции для модели",
    )

    DATASET_PATH: str = Field(
        description="Путь до датасета", default="./dataset/cv.json"
    )
    ENV: str = Field(description="Окружение: dev, prod", default="dev")
    PATH_TO_TEST_VACANCY: str = Field(
        description="Путь до тестовой вакансии",
        default="C:\\Users\\user\\source\\repos\\ai_hr\\ai_hr\\cv_ai\\src\\dataset\\вакансия.txt"
    )
    PATH_TO_TEST_RESUME: str = Field(
        description="Путь до тестового резюме",
        default="C:\\Users\\user\\source\\repos\\ai_hr\\ai_hr\\cv_ai\\src\\dataset\\резюме.txt"
    )


config = Config()