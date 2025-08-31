from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Запрос от Android клиента
class InterviewRequest(BaseModel):
    resume_text: str
    job_description: str

# Ответ от cv-ai-service
class CVAnalysisResult(BaseModel):
    approved: bool
    score: Optional[float] = None  # Общая оценка совпадения
    missing_skills: Optional[List[str]] = None
    matching_skills: Optional[List[str]] = None
    rejection_reason: Optional[str] = None # Причина, если approved=False

# Запрос к llm-service для генерации вопросов
class GenerateQuestionsRequest(BaseModel):
    resume_text: str
    job_description: str

# Ответ от llm-service с вопросами
class GeneratedQuestions(BaseModel):
    questions: List[str]

# Запрос к llm-service для финальной оценки
class FinalEvaluationRequest(BaseModel):
    resume_text: str
    job_description: str
    questions: List[str]  # Original questions
    user_answers: List[str] # User's answers

# Финальный ответ от llm-service
class FinalEvaluationResult(BaseModel):
    approved: bool
    score: Optional[float] = None
    correct_answers: Optional[int] = None
    total_questions: Optional[int] = None
    feedback: Optional[str] = None

# Ответ, который получит Android клиент
class InterviewResponse(BaseModel):
    status: str  # "rejected_after_cv", "rejected_after_interview", "approved"
    message: str
    details: Optional[Dict[str, Any]] = None
    questions: Optional[List[str]] = None # Только если status == "questions_generated"