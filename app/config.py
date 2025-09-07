from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    TG_TOKEN: str = Field(
        description="Токен для тг бота",
        default="8152863814:AAE_efaQn_0B3spZtcY2dIgEx3Mb07wiaoY",
    )
    OLLAMA_URL: AnyUrl = Field(default="http://localhost:11434")
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
    API_PORT: int = Field(description="Порт сервера uvicorn")


config = Config()  # type: ignore
