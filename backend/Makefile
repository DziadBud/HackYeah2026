.PHONY: venv run test up down hash-password

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

# usage: make hash-password EMAIL=admin@rops.krakow.pl
hash-password:
	.venv/bin/python -m app.cli.hash_admin_password $(EMAIL)
