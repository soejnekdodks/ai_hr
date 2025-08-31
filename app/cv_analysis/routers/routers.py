
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.cv_analysis.utils import extract_text
import requests
import json
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# URL внешнего нейросервиса
NEURAL_SERVICE_URL = "http://cv-ai-service:8001/analyze-text"

@router.post("/api/v1/analyze-cv")
async def analyze_cv(file: UploadFile = File(...), vacancy: str = Form(None)):
    """Анализ резюме: парсим файл и отправляем текст в нейросеть"""
    try:
        # Сохраняем временный файл
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Извлекаем текст из файла
        extracted_text = extract_text(temp_path)
        
        # Удаляем временный файл
        os.remove(temp_path)
        
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="Не удалось извлечь текст из файла")
        
        # Парсим вакансию, если передана
        vacancy_data = json.loads(vacancy) if vacancy else None
        
        # Отправляем текст в нейросеть для анализа
        payload = {
            "text": extracted_text,
            "vacancy": vacancy_data or {}
        }
        
        response = requests.post(
            NEURAL_SERVICE_URL,
            json=payload,
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            raise Exception(f"Нейросервис вернул ошибку: {response.status_code}")
        
        analysis_result = response.json()
        
        return {
            "service": "neural",
            "extracted_text_preview": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
            "analysis_result": analysis_result
        }
        
    except Exception as e:
        logger.error(f"CV analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))