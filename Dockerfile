FROM python:3.11.10-alpine3.20

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock ./

COPY . /app

RUN poetry install

ENTRYPOINT ["poetry", "run", "uvicorn", "src.gym_tracker.entrypoints.fastapi_app:app", "--host", "0.0.0.0", "--port", "5555", "--reload"]
