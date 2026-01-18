# Gym Tracker

## Alembic usage

Set the `DATABASE_URL` environment variable, then run migrations with Make targets or Alembic directly.

### Make targets

- `make db-upgrade` (upgrade to latest)
- `make db-downgrade` (downgrade one revision)
- `make db-stamp` (mark existing schema as current)
- `make db-revision` (autogenerate a new revision)

### Direct commands

- `poetry run alembic upgrade head`
- `poetry run alembic downgrade -1`
- `poetry run alembic stamp head`
- `poetry run alembic revision --autogenerate`
