from pydantic import BaseModel


class CVRequest(BaseModel):
    resume_text: str


class CVResponse(BaseModel):
    skills: list[str]
    experience: list[str]
    is_relevant: bool
