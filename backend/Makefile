.PHONY: venv run test up down

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
