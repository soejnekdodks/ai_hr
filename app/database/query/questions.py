from typing import Any

from sqlalchemy import select, update
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


async def set_answers(session: AsyncSession, update_data: list[dict[str, Any]]) -> None:
    await session.execute(update(Question), update_data)
    await session.flush()


async def all(session: AsyncSession):
    return [
        question.as_dict()
        for question in (await session.execute(select(Question))).scalars().all()
    ]
