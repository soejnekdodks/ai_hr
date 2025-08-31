FROM python:3.13-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.in-project true && \
    poetry install --without dev --no-interaction --no-root

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

COPY main.py ./
COPY . /app

CMD ["poetry", "run", "python", "main.py"]


FROM base AS production

RUN poetry install --no-interaction --no-cache --no-root --only main

COPY main.py ./
COPY . /app

CMD ["poetry", "run", "python", "main.py"]
