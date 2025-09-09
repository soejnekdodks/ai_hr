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
    changed_rows = (
        (await session.execute(update(Question).returning(Question.id), update_data))
        .scalars()
        .all
    )
    if len(changed_rows) != len(update_data):
        raise ValueError("Can't set all answers")
    await session.flush()


async def all(session: AsyncSession):
    return [
        question.as_dict()
        for question in (await session.execute(select(Question))).scalars().all()
    ]
