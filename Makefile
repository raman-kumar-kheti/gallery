.PHONY: help up down build migrate makemigrations worker shell-backend shell-db logs clean

DOCKER_COMPOSE = docker compose

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Start all services
	$(DOCKER_COMPOSE) up -d

down: ## Stop all services
	$(DOCKER_COMPOSE) down

build: ## Rebuild all images
	$(DOCKER_COMPOSE) build

logs: ## Tail logs from all services
	$(DOCKER_COMPOSE) logs -f

logs-backend: ## Tail backend logs
	$(DOCKER_COMPOSE) logs -f backend

logs-worker: ## Tail AI worker logs
	$(DOCKER_COMPOSE) logs -f ai-worker

migrate: ## Run Alembic migrations (inside backend container)
	$(DOCKER_COMPOSE) exec backend alembic upgrade head

makemigrations: ## Generate Alembic migration (MSG="description")
	$(DOCKER_COMPOSE) exec backend alembic revision --autogenerate -m "$(MSG)"

shell-backend: ## Open shell inside backend container
	$(DOCKER_COMPOSE) exec backend bash

shell-db: ## Open psql inside postgres container
	$(DOCKER_COMPOSE) exec postgres psql -U gallery -d gallery_db

worker: ## Start Celery worker locally (without Docker)
	cd apps/ai-worker && celery -A worker.celery_app worker --loglevel=info -Q ai_processing

flower: ## Start Flower monitoring locally
	cd apps/ai-worker && celery -A worker.celery_app flower

setup-env: ## Copy .env.example to .env
	cp .env.example .env
	@echo ".env created. Fill in your real values."

clean: ## Remove all containers, volumes, and generated files
	$(DOCKER_COMPOSE) down -v --remove-orphans
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true

install-backend: ## Install backend dependencies locally
	cd apps/backend-api && pip install -r requirements.txt

install-worker: ## Install AI worker dependencies locally
	cd apps/ai-worker && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd apps/frontend-web && npm install

install: install-backend install-worker install-frontend ## Install all dependencies
