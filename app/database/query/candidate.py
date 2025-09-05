from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.database.schema import Candidate


async def create(session: AsyncSession, cv: bytes) -> Candidate:
    candidate_obj = Candidate(cv=cv)
    session.add(candidate_obj)
    await session.flush()
    await session.refresh(candidate_obj)
    return candidate_obj


async def get_candidate(session: AsyncSession, candidate_id: int) -> Candidate | None:
    stmt = select(Candidate).where(Candidate.id == candidate_id).limit(1)
    return (await session.execute(stmt)).scalar()
