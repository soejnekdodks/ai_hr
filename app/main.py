from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.cv_analysis import cv_router

app = FastAPI(title="HR Assistant API", version="1.0.0")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутер CV анализа
app.include_router(cv_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "HR Assistant API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "cv-analysis"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)