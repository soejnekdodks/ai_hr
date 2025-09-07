FROM python:3.13-slim AS base

WORKDIR /app

ENV POETRY_HOME=/opt/poetry
ENV PATH="$POETRY_HOME/bin:$PATH"
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

RUN apt update && \
  apt install -y curl gcc g++ && \
  curl -sSL https://install.python-poetry.org | python - && \
  poetry --version

COPY pyproject.toml poetry.lock ./


FROM base AS development

RUN poetry install --no-interaction --no-cache --no-root 

COPY ./app /app/app
COPY ./alembic.ini .
COPY ./alembic /app/alembic
COPY ./cv_ai /app/cv_ai
COPY main.py .

CMD ["poetry", "run", "python", "/app/main.py"]


FROM base AS production

RUN poetry install --no-interaction --no-cache --no-root --only main

COPY ./app /app/app
COPY ./alembic.ini .
COPY ./alembic /app/alembic
COPY ./cv_ai /app/cv_ai
COPY main.py .

CMD ["poetry", "run", "python", "/app/main.py"]
