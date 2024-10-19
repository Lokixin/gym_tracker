ALL_PACKAGES := src tests

.PHONY : reformat lint unit app kill

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
