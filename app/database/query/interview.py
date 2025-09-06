from datetime import timedelta
from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.query.candidate import get_candidate
from app.database.schema import Interview, Question
from app.enums import InterviewState
from app.exceptions import CandidateNotFound


async def create(
    session: AsyncSession,
    candidate_id: int,
    questions: list[str],
    alias_id: UUID,
    expiration_time: timedelta | None = None,
) -> None:
    candidate = await get_candidate(session, candidate_id)
    if candidate is None:
        raise CandidateNotFound
    interview = Interview(
        expiration_time=expiration_time, candidate=candidate, alias_id=alias_id
    )
    session.add(interview)
    await session.flush()
    await session.refresh(interview)
    interview_id = interview.id
    await session.execute(
        insert(Question),
        [
            {"interview_id": interview_id, "question": question}
            for question in questions
        ],
    )
    await session.flush()


async def get_interview_by_alias(
    session: AsyncSession, alias_id: UUID
) -> Interview | None:
    stmt = (
        select(Interview)
        .where(Interview.alias_id == alias_id)
        .options(selectinload(Interview.questions))
        .limit(1)
    )
    return (await session.execute(stmt)).scalar()


async def mark_as_finished(session: AsyncSession, interview_id: int) -> None:
    stmt = (
        update(Interview)
        .where(Interview.id == interview_id)
        .values({Interview.state: InterviewState.FINISHED})
    )
    await session.execute(stmt)
    await session.flush()
