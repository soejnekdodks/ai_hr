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
    DATABASE_URL: str = Field(description="URL для доступа к бд")
    BOT_USERNAME: str = Field(description="Username бота в телеграм")
    LLM: str = Field(description="Используемая llm", default="llama3")
    API_PORT: int = Field(description="Порт сервера uvicorn")


config = Config()
