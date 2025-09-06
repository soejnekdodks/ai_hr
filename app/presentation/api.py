import os
import uuid

from answers_analize import AnswersAnalyzer
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.bot.start_bot import bot

from app.database import query
from app.database.core import get_async_session
from app.enums import InterviewState
from app.presentation.models import AnswersRequest, Question, QuestionsResponse

router = APIRouter()


@router.post("/api/v1/create-mock")
async def create_mock(session: AsyncSession = Depends(get_async_session)) -> str:
    candidate = await query.candidate.create(session, b"\x00" + os.urandom(4) + b"\x00")
    alias_id = uuid.uuid4()
    await query.interview.create(
        session,
        candidate.id,
        [
            "Что такое замыкание (closure) в JavaScript?",
            "Как избежать Callback Hell?",
            "Объясните принципы REST.",
            "Что такое миграции базы данных и зачем они нужны?",
            "Как вы обеспечиваете безопасность своего API?",
        ],
        alias_id,
    )
    await session.commit()
    return f"http://91.209.135.81/api/v1/deeplink?id={alias_id}"


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

    # Получаем chat_id HR-у, который связан с интервью
    candidate = interview.candidate
    hr_chat_id = candidate.chat_id
    if not hr_chat_id:
        raise HTTPException(status_code=404, detail="HR chat_id not found")

    # Анализируем ответы кандидата
    questions = [q.question for q in interview.questions]
    answers = [answer.answer for answer in data.answers]
    
    analyzer = AnswersAnalyzer()
    report = analyzer.analyze_answers(questions, answers)

    # Отправляем отчет HR-у
    await bot.send_message(hr_chat_id, report)

    # Сохраняем ответы кандидата в базе данных
    await query.questions.set_answers(
        session, [answer.model_dump() for answer in data.answers]
    )
    
    # Закрываем интервью
    await query.interview.mark_as_finished(session, interview.id)

    return Response(status_code=201)


@router.get("/api/v1/deeplink")
async def deeplink(id: str) -> None:
    return RedirectResponse(url=f"vtbhackaton://interview/{id}")


@router.get("/api/v1/all-questions")
async def get_all_questions(session: AsyncSession = Depends(get_async_session)):
    return await query.questions.all(session)
