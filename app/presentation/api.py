import os

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import query
from app.database.core import get_async_session
from app.enums import InterviewState
from app.presentation.models import QuestionsResponse, Question, AnswersRequest

router = APIRouter()


@router.post("/api/v1/create-mock")
async def create_mock(session: AsyncSession = Depends(get_async_session)) -> int:
    candidate = await query.candidate.create(
        session, "Test", "Testoviy", "Testovich", b"\x00" + os.urandom(4) + b"\x00"
    )
    interview_id = await query.interview.create(session, candidate.id)
    await session.commit()
    return interview_id


@router.get("/api/v1/questions")
async def get_questions(
    interview_id: int, session: AsyncSession = Depends(get_async_session)
):
    interview = await query.interview.get_interview(session, interview_id)
    if interview is None:
        raise HTTPException(status_code=404, detail="Interview not found")
    elif interview.state != InterviewState.OPEN:
        raise HTTPException(status_code=406, detail="Interview does not acceptable")
    return QuestionsResponse(questions=[Question(id=423, question="Хто ты?")])


@router.post("/api/v1/answers")
async def post_quentions(
    data: AnswersRequest, session: AsyncSession = Depends(get_async_session)
):
    interview = await query.interview.get_interview(session, data.interview_id)
    if interview is None:
        raise HTTPException(status_code=404, detail="Interview not found")
    elif interview.state != InterviewState.OPEN:
        raise HTTPException(
            status_code=406, detail="Interview saving does not acceptable"
        )
    return Response(status_code=201)
