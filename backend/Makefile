.PHONY: venv run test up down migrate openapi

venv:
	python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt

run:
	.venv/bin/uvicorn app.main:app --reload

test:
	.venv/bin/pytest

up:
	cd .. && docker compose up --build

down:
	cd .. && docker compose down

# re-apply match-api schema to the running db (idempotent; also runs on every `make up`)
migrate:
	cd .. && docker compose run --rm migrate

# api contract + swagger page in documentation/api; regenerate after any api change and commit them
openapi:
	DEBUG=false .venv/bin/python -m scripts.export_openapi
