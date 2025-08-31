from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.cv_analysis import cv_router

app = FastAPI(title="HR Assistant API", version="1.0.0")


@app.post("/analyze-resume/")
async def analyze_resume_endpoint(
    vacancy: VacancyRequest, resume_file: UploadFile = File(...)
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
