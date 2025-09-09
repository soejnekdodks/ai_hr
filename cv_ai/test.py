from answers_analize import AnswersAnalyzer
from cv_analyze import ResumeVacancyAnalyze
from questions_gen import QuestionsGenerator

resume = """
    Резюме кандидата. ФИО: Петров Алексей Сергеевич. Должность: Backend-разработчик (Node.js). Опыт: 3 года. Занятость: удаленная. 
    Контакты: email: petrov.a@mail.com, telegram: @alexey_petrov. 
    Навыки: JavaScript, TypeScript, Node.js, Express, NestJS, PostgreSQL, MongoDB, Redis, Docker, Jest, REST API, GraphQL. 
    Опыт работы: Компания "ТехноСистемы" (2021-настоящее время). Разработка API для маркетплейса. Оптимизация БД. Внедрение тестирования. Интеграция с Elasticsearch. 
    Образование: Университет ИТМО, бакалавр компьютерных наук. О себе: ответственный, инициативный, быстро учусь.
    """
vacancy = """
    Вакансия. Должность: Backend-разработчик (Node.js). Уровень: Middle. Формат: удаленно. Проект: SaaS-платформа с AI. 
    Обязанности: разработка backend, проектирование API, интеграция с сервисами, оптимизация производительности, код-ревью. 
    Требования: опыт Node.js от 2 лет, Express/Nest.js, PostgreSQL/MongoDB, REST API, Git, тестирование, Docker. 
    Плюсы: TypeScript, GraphQL, RabbitMQ/Kafka, микросервисы, AWS/GCP. Условия: график 10-19 МСК, оформление по ТК РФ, отпуск и больничные.
    """
questions = [
    "Что такое замыкание (closure) в JavaScript?",
    "Как избежать Callback Hell?",
    "Объясните принципы REST.",
    "Что такое миграции базы данных и зачем они нужны?",
    "Как вы обеспечиваете безопасность своего API?",
]
answers = [
    "Замыкание — это функция, которая имеет доступ к переменным из своего лексического окружения, даже после того, как внешняя функция завершила выполнение.",
    "Чтобы избежать Callback Hell, можно использовать Promises, async/await или разбивать функции на более мелкие и именованные.",
    "REST — архитектурный стиль, который использует HTTP-методы (GET, POST, PUT, DELETE) для операций с ресурсами, представленными в виде URI. Он stateless и ориентирован на ресурсы.",
    "Миграции — это система контроля версий для базы данных. Они позволяют последовательно применять и откатывать изменения схемы БД, что необходимо для командной разработки и развертывания.",
    "Безопасность API обеспечивается аутентификацией (JWT, OAuth), валидацией входящих данных, лимитом запросов (rate limiting), HTTPS и проверкой прав доступа (authorization) для каждого endpoint.",
]

cv_analyze = ResumeVacancyAnalyze()
print(cv_analyze.analyze_resume_vs_vacancy(resume, vacancy))
questions_gen = QuestionsGenerator()
print(questions_gen.generate_questions(resume, vacancy))
answers_analyze = AnswersAnalyzer()
print(answers_analyze.analyze_answers(questions, answers))
