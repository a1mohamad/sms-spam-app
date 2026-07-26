.DEFAULT_GOAL := help

PYTHON ?= python
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
COMPOSE ?= docker compose
API_PORT ?= 8000

.PHONY: help install install-dev install-convert run check \
	test test-unit test-api test-integration test-smoke test-local \
	compose-config build up down logs ps postgres migrate \
	migration-current migration-check convert-onnx validate-parity

help: ## Show the available shortcuts.
	@echo Setup
	@echo   make install              Install API runtime dependencies
	@echo   make install-dev          Install runtime and test dependencies
	@echo   make install-convert      Install model-conversion dependencies
	@echo Development
	@echo   make run                  Run the API locally with reload
	@echo   make check                Validate Compose and run safe tests
	@echo Tests
	@echo   make test                 Run tests without DB/deployment requirements
	@echo   make test-unit            Run unit tests
	@echo   make test-api             Run API tests
	@echo   make test-integration     Run artifact/model integration tests
	@echo   make test-smoke           Run local process smoke tests - requires DB
	@echo   make test-local           Run everything except deployment tests
	@echo Docker Compose
	@echo   make compose-config       Validate docker-compose.yml
	@echo   make build                Build the deployment image
	@echo   make up                   Build and start the full local stack
	@echo   make down                 Stop the stack without deleting DB data
	@echo   make logs                 Follow API logs
	@echo   make ps                   Show Compose service status
	@echo   make postgres             Start only local PostgreSQL
	@echo Database and model
	@echo   make migrate              Apply local Alembic migrations
	@echo   make migration-current    Show the local database revision
	@echo   make migration-check      Check for missing model migrations
	@echo   make convert-onnx         Export the Keras model to ONNX
	@echo   make validate-parity      Compare Keras and ONNX predictions

install: ## Install API runtime dependencies.
	$(PIP) install -r requirements.txt

install-dev: ## Install runtime and test dependencies.
	$(PIP) install -r requirements-dev.txt

install-convert: ## Install model-conversion dependencies.
	$(PIP) install -r requirements-convert.txt

run: ## Run the API locally with auto-reload.
	$(PYTHON) -m uvicorn app.main:app --reload --port $(API_PORT)

check: compose-config test ## Run the normal local validation set.

test: ## Run tests that need neither a live DB nor a deployment.
	$(PYTEST) -m "not database and not deployment"

test-unit: ## Run unit tests.
	$(PYTEST) tests/unit

test-api: ## Run API tests.
	$(PYTEST) tests/api

test-integration: ## Run non-database artifact and model integration tests.
	$(PYTEST) tests/integration -m "not database"

test-smoke: ## Run local process smoke tests; requires a migrated local DB.
	$(PYTEST) -m "smoke and not deployment"

test-local: ## Run the full local suite except container deployment tests.
	$(PYTEST) -m "not deployment"

compose-config: ## Validate the Docker Compose configuration.
	$(COMPOSE) config --quiet

build: ## Build the API deployment image.
	$(COMPOSE) build api

up: ## Build and start PostgreSQL, migrations, and the API.
	$(COMPOSE) up --build --wait

down: ## Stop the stack while preserving the PostgreSQL volume.
	$(COMPOSE) down

logs: ## Follow API container logs.
	$(COMPOSE) logs --follow api

ps: ## Show Compose service status.
	$(COMPOSE) ps --all

postgres: ## Start only the local PostgreSQL service.
	$(COMPOSE) up --detach --wait postgres

migrate: postgres ## Apply all pending migrations to local PostgreSQL.
	$(COMPOSE) run --rm migrate

migration-current: postgres ## Show the current local database revision.
	$(COMPOSE) run --rm migrate alembic current

migration-check: postgres ## Check ORM metadata against migration head.
	$(COMPOSE) run --rm migrate alembic check

convert-onnx: ## Export the configured Keras model to ONNX.
	$(PYTHON) scripts/convert_to_onnx.py

validate-parity: ## Validate numerical parity between Keras and ONNX.
	$(PYTHON) scripts/validate_keras_onnx_parity.py
