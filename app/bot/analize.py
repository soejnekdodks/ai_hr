from cv_ai.cv_analyze import ResumeVacancyAnalyze
from cv_ai.questions_gen import QuestionsGenerator
from cv_ai.answers_analize import AnswersAnalyzer
from aiogram import Router
from io import BytesIO
from app.bot.start_bot import bot
from app.database.query.candidate import create
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.database.core import get_async_session

router = Router()


async def analyze_resume(
    resume: str, vacancy: str, session: AsyncSession = Depends(get_async_session)
):
    cv_analyze = ResumeVacancyAnalyze()
    if cv_analyze.analyze_resume_vs_vacancy(resume, vacancy) > 70:
        return


questions_gen = QuestionsGenerator()
questions_gen.generate_questions(resume, vacancy)

answers_analyze = AnswersAnalyzer()
answers_analyze.analyze_answers(questions, answers)
