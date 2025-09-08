from ner import ResumeVacancyAnalyze


class ResumeVacancyMatcher:
    def __init__(self):
        self.parser = ResumeVacancyAnalyze()

    def match(self, resume_text: str, vacancy_text: str) -> float:
        # Получаем процент совпадения
        percentage = self.parser.analyze_resume_vs_job(resume_text, vacancy_text)
        # Возвращаем только число
        return percentage