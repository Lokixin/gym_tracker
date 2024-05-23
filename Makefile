ALL_PACKAGES := src tests

.PHONY : reformat lint unit

lint:
	poetry run ruff check $(ALL_PACKAGES) &
	poetry run mypy $(ALL_PACKAGES)

reformat:
	poetry run ruff format
unit:
	poetry run pytest .\tests\unit -s --log-level=INFO
