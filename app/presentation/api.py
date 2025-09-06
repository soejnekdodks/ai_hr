import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.start_bot import bot
from app.database import query
from app.database.core import get_async_session
from app.enums import InterviewState
from app.presentation.models import AnswersRequest, Question, QuestionsResponse
from cv_ai.answers_analize import AnswersAnalyzer

router = APIRouter()


@router.get("/api/v1/questions", response_model=QuestionsResponse)
async def get_questions(
    interview_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)
) -> QuestionsResponse:
    interview = await query.interview.get_interview_by_alias(session, interview_id)
    if interview is None:
        raise HTTPException(status_code=404, detail="Interview not found")
    elif interview.state != InterviewState.OPEN:
        raise HTTPException(status_code=406, detail="Interview does not acceptable")
    questions = await query.questions.get_questions(session, interview.id)
    return QuestionsResponse(
        questions=[
            Question(id=question.id, question=question.question)
            for question in questions
        ]
    )


@router.post("/api/v1/answers")
async def post_answers(
    data: AnswersRequest, session: AsyncSession = Depends(get_async_session)
) -> None:

    interview = await query.interview.get_interview_by_alias(session, data.interview_id)

    if interview is None:
        raise HTTPException(status_code=404, detail="Interview not found")

    if interview.state != InterviewState.OPEN:
        raise HTTPException(
            status_code=406, detail="Interview saving does not acceptable"
        )
    
    await session.refresh(interview, attribute_names=["candidate"])
    await session.refresh(interview.candidate, attribute_names=["chat"])
    candidate = interview.candidate
    hr_chat_id = candidate.chat.chat_id
    if not hr_chat_id:
        raise HTTPException(status_code=404, detail="HR chat_id not found")

    questions = [q.question for q in interview.questions]
    answers = [answer.answer for answer in data.answers]

    logger.info(answers)
    logger.info(f"Попытка отправки отчета в чат: {hr_chat_id}")
    logger.info(f"Тип chat_id: {type(hr_chat_id)}")
    logger.info(f"Данные кандидата: {candidate}")

    analyzer = AnswersAnalyzer()
    report = analyzer.analyze_answers(questions, answers)
    report = report + f"\nID кандидата: {candidate.id}"

    logger.info(report)

    await bot.send_message(int(hr_chat_id), report)

    await query.questions.set_answers(
        session, [answer.model_dump() for answer in data.answers]
    )

    await query.interview.mark_as_finished(session, interview.id)

    return Response(status_code=201)


@router.get("/api/v1/deeplink")
async def deeplink(id: str) -> None:
    return RedirectResponse(url=f"vtbhackaton://interview/{id}")
