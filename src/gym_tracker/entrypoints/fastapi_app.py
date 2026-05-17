from typing import Annotated

from fastapi import FastAPI, Depends
from starlette.staticfiles import StaticFiles

from gym_tracker.client.workouts_views import client_router
from gym_tracker.entrypoints.auth import oauth2_scheme, auth_router
from gym_tracker.entrypoints.search import search_router
from gym_tracker.entrypoints.workouts import workouts_router

app = FastAPI()
app.include_router(workouts_router)
app.include_router(search_router)
app.include_router(client_router)

app.include_router(auth_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/status")
def status() -> dict[str, str]:
    return {"message": "ok"}


@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}
