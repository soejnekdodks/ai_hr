from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.database.schema import Candidate, Chat



async def create(session: AsyncSession, cv: bytes, chat_id: str) -> Candidate:
    chat_obj = Chat(chat_id=chat_id)
    candidate_obj = Candidate(cv=cv, chat = chat_obj)
    session.add_all([candidate_obj, chat_obj])
    await session.flush()
    await session.refresh(candidate_obj)
    return candidate_obj


async def get_candidate(session: AsyncSession, candidate_id: int) -> Candidate | None:
    stmt = select(Candidate).where(Candidate.id == candidate_id).limit(1)
    return (await session.execute(stmt)).scalar()
