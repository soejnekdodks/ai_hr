from pydantic import Field


class Config(BaseConfig):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__change_documantation_urls()

    TG_TOKEN: str = Field(
        description="Токен для тг бота",
        default="8152863814:AAE_efaQn_0B3spZtcY2dIgEx3Mb07wiaoY",
    )
    HOST_URL: str = Field(
        description="URL по которому можно получить доступ к приложению"
    )
    OLLAMA_URL = "http://localhost:11434"
    MAX_FILE_SIZE_DOWNLOAD: int = Field(
        default=128 * 1024**2, description="Ограничение по загрузке в трекер в байтах"
    )
    DATABASE_URL: str = Field(description="URL для доступа к бд")
    BOT_USERNAME: str = Field(description="Username бота в телеграм")
    LLM: str = Field(description="Используемая llm", default="llama3")


config = Config()
