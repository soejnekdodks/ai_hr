from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.schema import Question


async def get_questions(session: AsyncSession, interview_id: int) -> list[Question]:
    return (
        (
            await session.execute(
                select(Question).where(Question.interview_id == interview_id)
            )
        )
        .scalars()
        .all()
    )
