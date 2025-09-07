from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    # Vikhrmodels/Vikhr-7B-instruct_0.4 если потяжелее
    # Vikhrmodels/Vikhr-Qwen-2.5-0.5b-Instruct легкая
    # Vikhrmodels/Vikhr-Llama-3.2-1B-Instruct средняя

    # Vikhrmodels/QVikhr-3-4B-Instruction

    BASE_MODEL: str = Field(
        default="Vikhrmodels/Vikhr-Qwen-2.5-0.5b-Instruct", description="Базовая модель"
    )

config = Config()
