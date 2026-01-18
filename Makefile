ALL_PACKAGES := src tests

.PHONY : reformat lint unit app kill docker-app down db-upgrade db-downgrade db-stamp db-revision


lint:
	poetry run ruff check $(ALL_PACKAGES) --fix &
	poetry run mypy $(ALL_PACKAGES)

reformat:
	poetry run ruff format

unit:
	poetry run pytest .\tests\unit -s --log-level=INFO

app:
	poetry run uvicorn src.gym_tracker.entrypoints.fastapi_app:app --host localhost --port 5555 --reload --log-level debug

kill:
	Stop-Process -Name "python" -force

docker-app:
	docker-compose up --build

down:
	docker-compose down

db-upgrade:
	poetry run alembic upgrade head

db-downgrade:
	poetry run alembic downgrade -1

db-stamp:
	poetry run alembic stamp head

db-revision:
	poetry run alembic revision --autogenerate
