.PHONY: install test lint run up bootstrap plan

install:      ## installe le service ingestion
	cd services/ingestion && pip install -e ".[dev]"

test:         ## lance les tests
	cd services/ingestion && pytest -v

lint:         ## ruff
	cd services/ingestion && ruff check src tests

run:          ## lance l'API en local
	cd services/ingestion && uvicorn ingestion.main:app --reload --port 8080

up:           ## stack docker-compose (api + postgres)
	docker compose up --build

bootstrap:    ## crée le backend Terraform (une seule fois)
	cd infra/bootstrap && terraform init && terraform apply

plan:         ## plan de l'env dev
	cd infra/envs/dev && terraform init && terraform plan
