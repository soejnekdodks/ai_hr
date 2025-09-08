include .env
include alembic/Makefile

DOCKER_COMPOSE_RUN=docker compose run --rm app

build:
	docker compose build

up:
	docker compose -f docker-compose.yml up --build
	docker compose down

format:
	- poetry run isort . --profile black
	- poetry run ruff format .

lint:
	poetry run ruff check .

fix:
	poetry run ruff check --fix .
	poetry run ruff format .

typecheck:
	poetry run pyright .

git:
	make format
	make lint
	make typecheck
