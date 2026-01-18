# AGENTS.md

This file provides guidance for agentic coding assistants working in this repository.
It summarizes build/lint/test commands and the expected code style.

## Project overview

- Python 3.11 project managed with Poetry.
- FastAPI entrypoint in `src/gym_tracker/entrypoints/fastapi_app.py`.
- Domain and service layers in `src/gym_tracker/domain` and `src/gym_tracker/services`.
- Postgres access via `psycopg` in `src/gym_tracker/adapters`.
- Tests live in `tests/` and are run with pytest.

## Quick start

1. Install dependencies: `poetry install`
2. Run the API: `poetry run uvicorn src.gym_tracker.entrypoints.fastapi_app:app --host localhost --port 5555 --reload --log-level debug`
3. Run unit tests: `poetry run pytest tests/unit -s --log-level=INFO`

## Commands (Makefile)

Use the Makefile where possible; it reflects the maintainer’s workflow.

- Lint: `make lint`
- Format: `make reformat`
- Unit tests: `make unit`
- Run app: `make app`
- Docker app: `make docker-app`
- Stop containers: `make down`

## Commands (direct Poetry)

### Formatting

- Format code: `poetry run ruff format`
- Format only a file: `poetry run ruff format src/gym_tracker/domain/model.py`

### Linting and type checking

- Ruff lint: `poetry run ruff check src tests`
- Ruff autofix: `poetry run ruff check src tests --fix`
- Mypy: `poetry run mypy src tests`

### Testing

- All tests: `poetry run pytest`
- Unit tests only: `poetry run pytest tests/unit -s --log-level=INFO`
- Single test file: `poetry run pytest tests/unit/test_workout_domain.py`
- Single test function: `poetry run pytest tests/unit/test_workout_domain.py::test_add_set_to_exercise`
- Match by name: `poetry run pytest tests/unit -k "workout"`

### Running the API

- Local dev server: `poetry run uvicorn src.gym_tracker.entrypoints.fastapi_app:app --host localhost --port 5555 --reload --log-level debug`
- Health check: `GET /status`

### Docker

- Build and run: `docker-compose up --build`
- Stop and clean: `docker-compose down`

## Code style guidelines

### Formatting

- Use Ruff for formatting (`ruff format`) and linting (`ruff check`).
- Keep line lengths consistent with Ruff defaults.
- Use double quotes only when a string needs escaping or matches existing context.
- Avoid inline comments unless specifically requested.

### Imports

- Use absolute imports from `gym_tracker` (e.g., `from gym_tracker.domain.model import Workout`).
- Keep imports grouped: standard library, third-party, local.
- Prefer explicit imports over wildcard imports.

### Types and annotations

- Add type annotations for public functions and methods.
- Use built-in generics (`list[str]`, `dict[str, int]`) instead of `typing.List`.
- Prefer `| None` for optional types, not `Optional`.
- Keep Pydantic DTOs explicit and minimal; keep domain models typed.

### Naming conventions

- Use `snake_case` for functions, methods, and variables.
- Use `PascalCase` for classes, Pydantic models, and dataclasses.
- Use `UPPER_SNAKE_CASE` for constants (e.g., `ALL_MUSCLES`).
- Route handlers should be verb-first (`get_`, `create_`, `add_`).

### Error handling and responses

- For API errors, raise `fastapi.HTTPException` with `starlette.status` codes.
- Return `JSONResponse` when you need explicit status codes or custom payloads.
- In services, keep data validation close to DTOs and repository boundaries.
- Avoid bare `except`; catch specific exceptions when needed.

### FastAPI patterns

- Use dependency injection with `Depends` for repository access.
- Keep routers in `src/gym_tracker/entrypoints` and include them in `fastapi_app.py`.
- Keep DTOs in `entrypoints/dtos.py` and domain models in `domain/model.py`.

### Repository and database access

- Repository methods should be small and focused on one query.
- Use `psycopg` `Connection` and context-managed cursors.
- Prefer parameterized queries; when interpolating SQL, ensure values are sanitized.
- Keep SQL strings in `adapters/*_queries.py` where possible.

### Testing style

- Use pytest fixtures from `tests/conftest.py` when helpful.
- Keep tests small and focused on one behavior.
- Name tests with `test_` prefixes and clear behavior descriptions.

## Cursor/Copilot rules

- No `.cursor/rules`, `.cursorrules`, or `.github/copilot-instructions.md` found.

## Notes for agentic assistants

- Do not add new dependencies without explicit request.
- Avoid changing public APIs unless requested.
- Keep edits minimal and consistent with the existing patterns.
- Do not commit changes unless explicitly asked.
