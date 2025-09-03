# app/config.py
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    # Основные настройки приложения
    APP_NAME: str = "AI HR Interview System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"  # development, staging, production
    
    # Настройки сервера
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    
    # CORS настройки
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # URL сервисов
    CV_AI_SERVICE_URL: str = "http://cv-ai-service:8001"
    LLM_SERVICE_URL: str = "http://llm-service:11434"
    
    # Настройки AI моделей
    LLM_MODEL_NAME: str = "llama3"
    CV_MODEL_PATH: str = "/app/models/cv_model"
    
    # Настройки времени ожидания
    HTTP_TIMEOUT: int = 30
    MODEL_TIMEOUT: int = 60
    
    # Настройки файлов
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["application/pdf"]
    
    # Пороги принятия решений
    CV_APPROVAL_THRESHOLD: float = 0.7
    INTERVIEW_APPROVAL_THRESHOLD: float = 0.6
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

# Создаем экземпляр настроек
settings = Settings()

# Функция для получения настроек (для Dependency Injection)
@lru_cache()
def get_settings() -> Settings:
    return Settings()