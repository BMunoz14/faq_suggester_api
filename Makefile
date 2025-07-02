SHELL := /usr/bin/env bash

## Variables
APP = app.main:app
UV := uv run uvicorn $(APP) --reload
PYTEST := python -m unittest discover -s tests -v

.PHONY: help dev test docker up down logs fmt

help:      ## Mostrar comandos disponibles
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?##"}; {printf " \033[36m%-15s\033[0m %s\n", $$1, $$2}'

dev:       ## Ejecutar API en modo desarrollo (hot-reload)
	$(UV)

test:      ## Ejecutar suite de tests (unittest)
	$(PYTEST)

ui:
	uv run streamlit run ui/streamlit_app.py

docker:    ## Construir imagen local faq-api:latest
	docker build -t faq-api .

up:        ## Levantar stack completo (API + Ollama)
	docker compose up --build

down:      ## Parar y eliminar contenedores
	docker compose down -v

logs:      ## Ver logs del contenedor API
	docker logs -f faq-api

fmt:       ## Formatear código con ruff & black (opcional)
	ruff check --fix .
	black .

