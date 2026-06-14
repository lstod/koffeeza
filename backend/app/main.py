from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from alembic import command
from app.config import ALLOWED_ORIGINS
from app.routers import beans, grinders, machines, preferences, recall, shots, users


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")
    yield


app = FastAPI(title="Koffeeza", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(beans.router)
app.include_router(grinders.router)
app.include_router(machines.router)
app.include_router(shots.router)
app.include_router(recall.router)
app.include_router(preferences.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
