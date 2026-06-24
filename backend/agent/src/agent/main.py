"""FastAPI application."""

import subprocess
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent.api.routes import agent, clients
from agent.api.routes import settings as settings_routes
from agent.config import settings
from agent.logging_config import setup_logging
from agent.persistence.database import engine


def run_migrations() -> None:
    subprocess.run(["alembic", "upgrade", "head"], check=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    run_migrations()
    yield
    await engine.dispose()


app = FastAPI(title="Agent Service", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(agent.router)
app.include_router(clients.router)
app.include_router(settings_routes.router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
