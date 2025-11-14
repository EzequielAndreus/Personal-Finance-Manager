# Makefile for Flask Application Docker Management

.PHONY: help build up down logs shell db-shell test clean prod-up prod-down migrate

# Default target
help:
	@echo "Available commands:"
	@echo "  build      - Build Docker images"
	@echo "  up         - Start development environment"
	@echo "  down       - Stop development environment"
	@echo "  logs       - View container logs"
	@echo "  shell      - Access Flask container shell"
	@echo "  db-shell   - Access PostgreSQL shell"
	@echo "  test       - Run tests in Docker"
	@echo "  clean      - Clean up containers and volumes"
	@echo "  prod-up    - Start production environment"
	@echo "  prod-down  - Stop production environment"
	@echo "  migrate    - Run database migrations"

# Development environment
build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

shell:
	docker compose exec web bash

db-shell:
	docker compose exec db psql -U postgres -d postgres

# Testing (inside docker)
test:
	docker compose exec web uv run pytest

test-unit:
	docker compose exec web uv run pytest -m unit

test-integration:
	docker compose exec web uv run pytest -m integration

test-cov:
	docker compose exec web uv run pytest --cov=src --cov=models --cov-report=term-missing

# Production environment
prod-up:
	docker compose -f docker-compose.prod.yml up -d

prod-down:
	docker compose -f docker-compose.prod.yml down

# Database operations
migrate:
	docker compose exec web uv run python -c "from src.app import create_app; from src.models import db; app = create_app(); app.app_context().push(); db.create_all()"

# Cleanup
clean:
	docker compose down -v
	docker system prune -f

clean-all:
	docker compose down -v --rmi all
	docker system prune -af

# Development helpers
restart:
	docker compose restart

restart-web:
	docker compose restart web

# Status
status:
	docker compose ps
