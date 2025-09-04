from pydantic import Field
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


load_dotenv()

class Config(BaseSettings):
    HOST_URL: str = Field(
        description="URL по которому можно получить доступ к приложению",
        default="http://localhost",
    )

    TG_TOKEN: str = Field(description="Токен для тг бота", default="")
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


config = Config()  # type: ignore
