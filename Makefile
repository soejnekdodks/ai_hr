include .env
include alembic/Makefile

DOCKER_COMPOSE=docker compose -f docker-compose.yml
DOCKER_COMPOSE_RUN=${DOCKER_COMPOSE} run --rm reg-bot
DOCKER_COMPOSE_RUN_TESTS=${DOCKER_COMPOSE} -f docker-compose-test.yml run --rm reg-bot
VOLUMES=pg_data mongo_data rabbitmq_data
VOLUMES_TEST=pg_data_test mongo_data_test rabbitmq_data_test

build:
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up --build
	docker compose down

up-prod:
	docker compose -f docker-compose-prod.yml up --build -d

test: upgrade_head_test
	- $(DOCKER_COMPOSE_RUN_TESTS) pytest -vv -s --disable-warnings tests
	- docker compose down
	- sleep 0.1 && docker volume rm $(VOLUMES_TEST)

clear:
	- docker compose down
	- docker volume rm $(VOLUMES)

format:
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
	make test
