from fastapi import FastAPI

from gym_tracker.entrypoints.search import search_router
from gym_tracker.entrypoints.workouts import workouts_router

app = FastAPI()
app.include_router(workouts_router)
app.include_router(search_router)


@app.get("/status")
def status() -> dict[str, str]:
    return {"message": "ok"}
