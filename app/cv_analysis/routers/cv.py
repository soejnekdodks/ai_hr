from fastapi import APIRouter
from models import CVAnalysisResult  # Импортируем общую модель
# ... ваш импорт для анализа резюме ...

router = APIRouter()

@router.post("/analyze_cv", response_model=CVAnalysisResult)
async def analyze_cv_endpoint(resume_text: str, job_description: str):
    """
    Эндпоинт для анализа резюме.
    """
    # Здесь ваша логика анализа резюме с помощью ML моделей
    is_approved, score, missing_skills, matching_skills = await analyze_resume(resume_text, job_description)

    result = CVAnalysisResult(
        approved=is_approved,
        score=score,
        missing_skills=missing_skills,
        matching_skills=matching_skills
    )

    if not is_approved:
        result.rejection_reason = "Несоответствие ключевым требованиям вакансии."

    return result