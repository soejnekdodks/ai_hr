from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    BASE_MODEL: str = Field(
        default="Vikhrmodels/Vikhr-7B-instruct_0.4", description="Базовая модель"
    )


config = Config()
