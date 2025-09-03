from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.models import VacancyRequest, DialogAnalysisRequest
from app.cv_analysis.analyzer import analyze_resume
from app.dialog_analysis.analyzer import analyze_dialog
import tempfile
import os

app = FastAPI(title="AI HR System", version="1.0.0")

@app.post("/analyze-resume/")
async def analyze_resume_endpoint(
    vacancy: VacancyRequest,
    resume_file: UploadFile = File(...)
):
    try:
        # Сохраняем временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await resume_file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Анализируем резюме
        result = analyze_resume(tmp_path, vacancy.dict())
        
        # Удаляем временный файл
        os.unlink(tmp_path)
        
        return JSONResponse(content=result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-dialog/")
async def analyze_dialog_endpoint(request: DialogAnalysisRequest):
    try:
        result = analyze_dialog(request.dialog, request.criteria)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}