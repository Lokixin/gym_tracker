Configuration
=============

The application reads runtime settings from environment variables.

- `DATABASE_URL`: SQLAlchemy database URL. Defaults to `postgresql+psycopg://admin:admin@postgres/workouts` for the Docker local setup.
- `STRENGTHLOG_COOKIE`: optional cookie header for the exercise ingestion scraper. Leave unset unless the scraper needs an authenticated/session cookie.

Alembic also requires `DATABASE_URL` because `alembic.ini` intentionally does not commit a database URL.
