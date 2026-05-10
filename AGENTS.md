# AGENTS.md

## Commands

- Install deps: `poetry install`
- Run app: `make app` or `poetry run uvicorn src.gym_tracker.entrypoints.fastapi_app:app --host localhost --port 5555 --reload --log-level debug`
- Unit tests: `make unit` or `poetry run pytest .\tests\unit -s --log-level=INFO`
- Focused test: `poetry run pytest tests/unit/test_workout_domain.py::test_add_set_to_exercise`
- Format: `make reformat` or `poetry run ruff format`
- Non-mutating lint: `poetry run ruff check src tests`
- Typecheck: `poetry run mypy src tests`
- `make lint` runs `ruff check src tests --fix` and mypy, so it may edit files.
- Docker app/db/adminer: `make docker-app`; stop with `make down`.

## App Shape

- FastAPI entrypoint: `src/gym_tracker/entrypoints/fastapi_app.py`.
- Routers: `/workouts` in `entrypoints/workouts.py`, `/search` in `entrypoints/search.py`, HTML client routes under `/app` in `client/workouts_views.py`.
- Static files are mounted from root `static/`; templates are loaded from root `templates/`.
- Service logic lives in `src/gym_tracker/services`; persistence lives in `src/gym_tracker/adapters`.

## Database

- Runtime DB settings are hard-coded in `src/gym_tracker/entrypoints/dependencies.py`: psycopg connection string plus SQLAlchemy URL using host `postgres` and database `workouts`.
- `PostgresSQLRepo` currently mixes raw `psycopg` queries from `adapters/*_queries.py` with SQLAlchemy `Session` operations; avoid assuming a single DB style.
- Alembic requires `DATABASE_URL`; `alembic.ini` intentionally leaves `sqlalchemy.url` empty.
- Migration commands: `make db-upgrade`, `make db-downgrade`, `make db-stamp`, `make db-revision`.

## Models And Tests

- Legacy domain dataclasses/enums used by unit tests and DTO mapping are in `src/gym_tracker/domain/model.py`.
- SQLAlchemy ORM models used by Alembic are in `src/gym_tracker/domain/models/` and share `domain.models.base.Base`.
- Tests currently live only under `tests/unit`; shared fixtures are in `tests/conftest.py`.
