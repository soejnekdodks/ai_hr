import os

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import query
from app.database.core import get_async_session
from app.enums import InterviewState
from app.presentation.models import AnswersRequest, Question, QuestionsResponse

router = APIRouter()


@router.post("/api/v1/create-mock")
async def create_mock(session: AsyncSession = Depends(get_async_session)) -> int:
    candidate = await query.candidate.create(session, b"\x00" + os.urandom(4) + b"\x00")
    interview_id = await query.interview.create(session, candidate.id)
    await session.commit()
    return interview_id


@router.get("/api/v1/questions", response_model=QuestionsResponse)
async def get_questions(
    interview_id: int, session: AsyncSession = Depends(get_async_session)
) -> QuestionsResponse:
    interview = await query.interview.get_interview(session, interview_id)
    if interview is None:
        raise HTTPException(status_code=404, detail="Interview not found")
    elif interview.state != InterviewState.OPEN:
        raise HTTPException(status_code=406, detail="Interview does not acceptable")
    return QuestionsResponse.model_validate(
        {
            "questions": [
                {"id": 0, "question": "Что такое замыкание (closure) в JavaScript?"},
                {"id": 1, "question": "Как избежать Callback Hell?"},
                {"id": 2, "question": "Объясните принципы REST."},
                {
                    "id": 3,
                    "question": "Что такое миграции базы данных и зачем они нужны?",
                },
                {"id": 4, "question": "Как вы обеспечиваете безопасность своего API?"},
            ]
        }
    )


@router.post("/api/v1/answers")
async def post_quentions(
    data: AnswersRequest, session: AsyncSession = Depends(get_async_session)
) -> None:
    interview = await query.interview.get_interview(session, data.interview_id)
    if interview is None:
        raise HTTPException(status_code=404, detail="Interview not found")
    elif interview.state != InterviewState.OPEN:
        raise HTTPException(
            status_code=406, detail="Interview saving does not acceptable"
        )
    await query.interview.mark_as_finished(session, interview.id)
    return Response(status_code=201)


@router.get("/api/v1/deeplink")
async def deeplink() -> None:
    return RedirectResponse(url="vtbhackaton://interview/123")
