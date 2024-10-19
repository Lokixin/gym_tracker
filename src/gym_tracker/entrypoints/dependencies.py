import psycopg

from gym_tracker.adapters.repositories import PostgresSQLRepo

connection_string = "dbname=workouts host=postgres user=admin password=admin"

postgres_client = psycopg.connect(connection_string, autocommit=True)


def get_workouts_repo() -> PostgresSQLRepo:
    return PostgresSQLRepo(postgres_client)
