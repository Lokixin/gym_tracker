from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from gym_tracker.client.workouts_views import client_router
from gym_tracker.entrypoints.search import search_router
from gym_tracker.entrypoints.workouts import workouts_router

app = FastAPI()
app.include_router(workouts_router)
app.include_router(search_router)
app.include_router(client_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/status")
def status() -> dict[str, str]:
    return {"message": "ok"}
