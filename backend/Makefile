.PHONY: venv run test up down hash-password migrate

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

# usage: make hash-password EMAIL=admin@rops.krakow.pl
hash-password:
	.venv/bin/python -m app.cli.hash_admin_password $(EMAIL)
