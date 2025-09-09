import uuid

from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class BaseScheme(BaseModel):
    class Config:
        alias_generator = to_camel
        populate_by_name = True


class Question(BaseScheme):
    id: int
    question: str


class QuestionsResponse(BaseScheme):
    questions: list[Question]


class Answer(BaseScheme):
    id: int
    answer: str


class AnswersRequest(BaseScheme):
    interview_id: uuid.UUID
    answers: list[Answer]
