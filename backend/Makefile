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

# apply match-api schema to a running local db (idempotent; one file per table)
migrate:
	@for f in sql/*.sql; do \
		echo "=== $$f ==="; \
		docker exec -i hackyeah-db psql -U hackyeah -d hackyeah -v ON_ERROR_STOP=1 < "$$f"; \
	done

# api contract for the frontend; regenerate after any api change and commit it
openapi:
	DEBUG=false .venv/bin/python -c "import json; from app.main import app; print(json.dumps(app.openapi(), indent=2, ensure_ascii=False))" > openapi.json
