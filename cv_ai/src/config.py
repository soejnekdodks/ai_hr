from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):

    # Базовая модель DeepSeek (Hugging Face)
    BASE_MODEL: str = Field(
        default="Vikhrmodels/Vikhr-7B-instruct_0.4",
        description="Базовая модель"
    )

config = Config()