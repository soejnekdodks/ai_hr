import uvicorn
from fastapi import FastAPI
from cv_analysis.routers import cv
from dialog_analysis.routers import llm
from config import settings

# Создаем основное приложение
app = FastAPI(
    title="AI HR Interview System",
    description="Система для автоматического проведения собеседований с AI",
    version="1.0.0"
)

# Подключаем роутеры
app.include_router(cv.router)
app.include_router(llm.router)

@app.get("/")
async def root():
    return {
        "message": "AI HR Interview System is running",
        "docs": "/docs",
        "cv_service": f"{settings.CV_AI_SERVICE_URL}/docs",
        "llm_service": f"{settings.LLM_SERVICE_URL}"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "main-app"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )