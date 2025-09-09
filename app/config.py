from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Загружаем переменные окружения ДО создания конфига
load_dotenv()


class Config(BaseSettings):
    TG_TOKEN: str = Field(
        description="Токен для тг бота",
        default="8152863814:AAE_efaQngEx3Mb07wiaoY",
    )
    MAX_FILE_SIZE_DOWNLOAD: int = Field(
        default=128 * 1024**2, description="Ограничение по загрузке в трекер в байтах"
    )

    PG_NAME: str = Field(description="Название бд в postgresql", default="pg_name")
    PG_LOGIN: str = Field(description="Логин бд в postgresql", default="pg_log")
    PG_PASSWORD: str = Field(description="Пароль бд в postgresql", default="pg_pass")

    OLLAMA_URL: str = Field(
        description="URL для подключения к ollama", default="http://localhost:11434"
    )
    LLM: str = Field(description="Используемая llm", default="llama3")
    API_PORT: int = Field(
        description="Порт сервера uvicorn",
        default=8000,  # Добавлено значение по умолчанию
    )
    DATABASE_URL: str = Field(
        description="URL базы данных",
        default="postgresql+asyncpg://pg_log:pg_pass@localhost:5432/pg_name",
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


config = Config()
