# dialog_analysis/routers/analyzer.py
from fastapi import APIRouter, HTTPException
from models import GenerateQuestionsRequest, GeneratedQuestions, FinalEvaluationRequest, FinalEvaluationResult
import httpx

router = APIRouter()
OLLAMA_BASE_URL = "http://localhost:11434"  # Внутри контейнера llm-service

@router.post("/api/generate_questions")
async def generate_questions(request: GenerateQuestionsRequest):
    """
    Генерация вопросов на основе резюме и вакансии.
    """
    prompt = f"""
    [INSTRUCTION]
    Ты - HR-специалист. На основе резюме кандидата и описания вакансии сгенерируй 5 точных и релевантных вопросов для собеседования.
    Верни ТОЛЬКО список вопросов, без номеров, без дополнительного текста, каждый вопрос с новой строки.

    [RESUME]
    {request.resume_text}

    [JOB DESCRIPTION]
    {request.job_description}

    [QUESTIONS]
    """

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            llm_output = response.json()["response"].strip()

            # Парсим ответ LLM (предполагаем, что каждый вопрос на новой строке)
            questions = [q.strip() for q in llm_output.split('\n') if q.strip()]
            return GeneratedQuestions(questions=questions[:5])  # Берем не более 5 вопросов

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации вопросов: {str(e)}")

@router.post("/api/evaluate_answers")
async def evaluate_answers(request: FinalEvaluationRequest):
    """
    Финальная оценка кандидата на основе ответов.
    """
    # Формируем детальный промпт для оценки
    answers_context = "\n".join(
        [f"Вопрос: {q}\nОтвет: {a}\n" for q, a in zip(request.questions, request.user_answers)]
    )

    prompt = f"""
    [INSTRUCTION]
    Ты - старший HR-специалист. Проанализируй ответы кандидата на собеседовании.
    Оцени, прошел ли кандидат собеседование (approved: true/false).
    Верни ответ в формате JSON строго по схеме:
    {{
        "approved": boolean,
        "score": number (0-100),
        "correct_answers": number,
        "total_questions": number,
        "feedback": string
    }}

    [RESUME]
    {request.resume_text}

    [JOB DESCRIPTION]
    {request.job_description}

    [Q&A]
    {answers_context}

    [JSON]
    """

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "format": "json",  # Важно: просим модель вернуть JSON
                    "stream": False
                }
            )
            response.raise_for_status()
            llm_output = response.json()["response"].strip()

            # Пытаемся распарсить JSON ответ модели
            import json
            evaluation = json.loads(llm_output)
            return FinalEvaluationResult(**evaluation)

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="LLM вернул некорректный JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка оценки ответов: {str(e)}")