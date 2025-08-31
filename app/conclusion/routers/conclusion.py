from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
import httpx
from config import settings
from parsing import extract_text_from_pdf
from models import (
    InterviewRequest, InterviewResponse, CVAnalysisResult,
    GenerateQuestionsRequest, GeneratedQuestions,
    FinalEvaluationRequest, FinalEvaluationResult
)

router = APIRouter(prefix="/conclusion", tags=["conclusion"])

@router.post("/start_interview", response_model=InterviewResponse)
async def start_interview_flow(
    resume_pdf: UploadFile = File(..., description="PDF файл с резюме"),
    job_description: str = Form(..., description="Описание вакансии")
):
    """
    Главный эндпоинт, который запускает весь процесс собеседования.
    Принимает PDF файл с резюме и описание вакансии.
    """
    # Проверяем, что файл PDF
    if resume_pdf.content_type != "application/pdf":
        raise HTTPException(
            status_code=400, 
            detail="Файл должен быть в формате PDF"
        )

    # Извлекаем текст из PDF
    resume_text = await extract_text_from_pdf(resume_pdf)
    
    # Дальше используем существующую логику
    async with httpx.AsyncClient() as client:
        try:
            # Шаг 1: Анализ резюме
            cv_analysis_url = f"{settings.CV_AI_SERVICE_URL}/analyze_cv"
            cv_payload = {
                "resume_text": resume_text,
                "job_description": job_description
            }
            cv_response = await client.post(cv_analysis_url, json=cv_payload)
            cv_response.raise_for_status()
            cv_result = CVAnalysisResult(**cv_response.json())

            # ... остальная логика без изменений ...
            if not cv_result.approved:
                return InterviewResponse(
                    status="rejected_after_cv",
                    message="Кандидат не прошел первичный отбор по резюме.",
                    details={
                        "score": cv_result.score,
                        "missing_skills": cv_result.missing_skills,
                        "rejection_reason": cv_result.rejection_reason
                    }
                )

            # Шаг 3: Генерация вопросов
            gen_questions_url = f"{settings.LLM_SERVICE_URL}/api/generate_questions"
            questions_request = GenerateQuestionsRequest(
                resume_text=resume_text,
                job_description=job_description
            )
            questions_response = await client.post(gen_questions_url, json=questions_request.dict())
            questions_response.raise_for_status()
            questions_data = GeneratedQuestions(**questions_response.json())

            return InterviewResponse(
                status="questions_generated",
                message="Пожалуйста, ответьте на вопросы.",
                questions=questions_data.questions
            )

        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Ошибка связи с AI-сервисом: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

@router.post("/submit_answers", response_model=InterviewResponse)
async def submit_answers(
    questions: List[str], 
    user_answers: List[str], 
    resume_text: str = Form(...),
    job_description: str = Form(...)
):
    """
    Эндпоинт для отправки ответов пользователя и получения финального вердикта.
    Принимает текст резюме и вакансии, так как они нужны для финальной оценки.
    """
    if len(questions) != len(user_answers):
        raise HTTPException(status_code=400, detail="Количество вопросов и ответов не совпадает.")

    async with httpx.AsyncClient() as client:
        try:
            # Шаг 4: Финальная оценка ответов
            final_eval_url = f"{settings.LLM_SERVICE_URL}/api/evaluate_answers"
            eval_request = FinalEvaluationRequest(
                resume_text=resume_text,
                job_description=job_description,
                questions=questions,
                user_answers=user_answers
            )
            eval_response = await client.post(final_eval_url, json=eval_request.dict())
            eval_response.raise_for_status()
            final_result = FinalEvaluationResult(**eval_response.json())

            # Формируем финальный ответ
            if final_result.approved:
                return InterviewResponse(
                    status="approved",
                    message="Поздравляем! Кандидат успешно прошел собеседование.",
                    details={
                        "score": final_result.score,
                        "correct_answers": final_result.correct_answers,
                        "total_questions": final_result.total_questions,
                        "feedback": final_result.feedback
                    }
                )
            else:
                return InterviewResponse(
                    status="rejected_after_interview",
                    message="Кандидат не прошел собеседование.",
                    details={
                        "score": final_result.score,
                        "correct_answers": final_result.correct_answers,
                        "total_questions": final_result.total_questions,
                        "feedback": final_result.feedback
                    }
                )

        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Ошибка связи с AI-сервисом: {str(e)}")