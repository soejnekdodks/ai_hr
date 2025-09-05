from main_pipeline import ResumeVacancyMatcher

def cv_analize(resume_text: str, vacancy_text: str):
    matcher = ResumeVacancyMatcher()
    result = matcher.match(resume_text, vacancy_text)

    return result