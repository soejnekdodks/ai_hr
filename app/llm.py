from app.config import config
from fastapi import APIRouter, HTTPException
import httpx
from loguru import logger


router = APIRouter()

async def make_request_to_llm(prompt: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config.OLLAMA_URL}/api/generate",
                json={"model": config.LLM, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            llm_output = response.json()["response"].strip()
            return llm_output
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка генерации вопросов: {str(e)}"
        )


async def generate_questions(cv: str, vaca: str) -> list[str]:
    prompt = f"""
    [INSTRUCTION]
    Ты - HR-специалист. На основе резюме кандидата и описания вакансии сгенерируй 5 точных и релевантных вопросов для собеседования.
    Верни ТОЛЬКО список вопросов, без номеров, без дополнительного текста, каждый вопрос с новой строки.

    [RESUME]
    {cv}

    [JOB DESCRIPTION]
    {vaca}
    """
    response = await make_request_to_llm(prompt=prompt)
    return response.split("\n")


async def evaluate_answers(
    cv: str, vaca: str, questions: list[str], answers: list[str]
) -> dict:
    answers_context = "\n".join(
        [f"Вопрос: {q}\nОтвет: {a}\n" for q, a in zip(questions, answers)]
    )

    prompt = f"""
    [INSTRUCTION]
    Ты - HR-специалист. Проанализируй ответы кандидата на собеседовании.
    Оцени, прошел ли кандидат собеседование (approved: true/false).
    Верни ответ в формате JSON СТРОГО по схеме:
    {{
        "approved": boolean,
        "score": number (0-100),
        "correct_answers": integer number,
        "total_questions": integer number,
        "feedback": string
    }}

    [RESUME]
    {cv}

    [JOB DESCRIPTION]
    {vaca}

    [Q&A]
    {answers_context}
    """
    response = await make_request_to_llm(prompt=prompt)
    try:
        response = dict(response)
        return response
    except Exception:
        logger.info("Ответ от llm нельзя преобразовать в json")
        return None
