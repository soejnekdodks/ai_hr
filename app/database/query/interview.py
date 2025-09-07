from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.database.query.candidate import get_candidate
from app.database.schema import Interview
from app.exceptions import CandidateNotFound


async def create(
    session: AsyncSession, candidate_id: int, expiration_time: timedelta | None = None
) -> int:
    candidate = await get_candidate(session, candidate_id)
    if candidate is None:
        raise CandidateNotFound
    interview = Interview(expiration_time=expiration_time, candidate=candidate)
    session.add(interview)
    await session.flush()
    await session.refresh(interview)
    return interview.id


async def get_interview(session: AsyncSession, interview_id: int) -> Interview | None:
    stmt = select(Interview).where(Interview.id == interview_id).limit(1)
    return (await session.execute(stmt)).scalar()
