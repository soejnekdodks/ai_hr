from sqlalchemy.ext.asyncio import AsyncSession

from app.database.schema import Question


async def add_questions(session: AsyncSession) -> None:
    pass


async def add_answers(session: AsyncSession) -> None:
    pass
