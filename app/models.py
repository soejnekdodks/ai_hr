from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class VacancyRequest(BaseModel):
    job_title: str
    required_skills: List[str]
    nice_to_have_skills: List[str] = Field(default_factory=list)
    required_experience: int
    education_level: Optional[str] = None


class Criteria(BaseModel):
    name: str
    weight: float = 1.0
    description: Optional[str] = None


class DialogTurn(BaseModel):
    speaker: str
    text: str
    timestamp: Optional[str] = None


class DialogAnalysisRequest(BaseModel):
    dialog: List[DialogTurn]
    criteria: List[Criteria]
    candidate_id: Optional[str] = None


class AnalysisResult(BaseModel):
    candidate_id: str
    overall_score: float
    skills_match: Dict[str, float]
    missing_skills: List[str]
    recommendation: str
    details: Dict
