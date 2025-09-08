from ner import ResumeParser


class ResumeVacancyMatcher:
    def __init__(self):
        self.parser = ResumeParser()

    def match(self, resume_text: str, vacancy_text: str) -> float:
        # Получаем процент совпадения
        percentage = self.parser.evaluate_match(resume_text, vacancy_text)
        # Возвращаем только число
        return percentage