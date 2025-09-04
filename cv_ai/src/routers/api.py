from .models import CVRequest, CVResponse
from fastapi import APIRouter


router = APIRouter()


@router.post("/api/v1/cv_analyze")
async def analyze_cv(request: CVRequest):
    entities = analyze_cv_pipeline(request.resume_text)
    skills = [e["word"] for e in entities if e["entity_group"] == "SKILL"]
    experience = [e["word"] for e in entities if e["entity_group"] == "EXP"]
    is_relevant = len(skills) > 5

    return CVResponse(skills=skills, experience=experience, is_relevant=is_relevant)
