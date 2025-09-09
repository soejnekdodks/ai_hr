import uuid
from datetime import datetime, timedelta

from sqlalchemy import TEXT, UUID, ForeignKey, Interval, LargeBinary, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.core import Base
from app.enums import InterviewState


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    chat_id: Mapped[str] = mapped_column()

    candidates: Mapped[list["Candidate"]] = relationship(
        back_populates="chat", cascade="all, delete-orphan"
    )


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    cv: Mapped[bytes | None] = mapped_column(LargeBinary)

    interview_id: Mapped[int | None] = mapped_column(
        ForeignKey("interviews.id", ondelete="CASCADE"), unique=True
    )
    interview: Mapped["Interview"] = relationship(
        back_populates="candidate",
        uselist=False,
    )

    chat_id: Mapped[int | None] = mapped_column(
        ForeignKey("chats.id", ondelete="CASCADE")
    )
    chat: Mapped[Chat] = relationship(back_populates="candidates")


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    expiration_time: Mapped[timedelta | None] = mapped_column(Interval)
    state: Mapped[InterviewState] = mapped_column(default=InterviewState.OPEN)
    alias_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    candidate: Mapped[Candidate] = relationship(
        back_populates="interview",
        uselist=False,
    )
    questions: Mapped[list["Question"]] = relationship(back_populates="interview")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    question: Mapped[str] = mapped_column()
    answer: Mapped[str | None] = mapped_column(TEXT)

    interview_id: Mapped[int | None] = mapped_column(ForeignKey("interviews.id"))
    interview: Mapped[Interview] = relationship(back_populates="questions")
