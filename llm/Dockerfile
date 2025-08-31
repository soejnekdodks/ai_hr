FROM python:3.13-slim AS base

WORKDIR /app

ENV POETRY_HOME=/opt/poetry
ENV PATH="$POETRY_HOME/bin:$PATH"
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

RUN apt update && \
  apt install -y curl && \
  curl -sSL https://install.python-poetry.org | python - && \
  poetry --version

COPY pyproject.toml poetry.lock ./


FROM base AS development

RUN poetry install --no-interaction --no-cache --no-root 

COPY alembic.ini main.py ./
COPY ./src ./src
COPY ./alembic ./alembic

CMD ["poetry", "run", "python", "main.py"]


FROM base AS production

RUN poetry install --no-interaction --no-cache --no-root --only main

COPY alembic.ini main.py ./
COPY ./src ./src
COPY ./alembic ./alembic

CMD ["poetry", "run", "python", "main.py"]
