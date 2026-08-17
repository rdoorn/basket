.PHONY: build up down logs restart ps test-backend

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

restart: down up

ps:
	docker compose ps

test-backend:
	cd backend && uv run pytest -v && uv run flake8 app tests
