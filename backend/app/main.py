"""FastAPI application for the wisata search engine backend.

Instantiates the FastAPI app, configures CORS middleware for frontend
communication, manages the Elasticsearch client lifecycle through a lifespan
context, and includes the API router under the /api prefix.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import router


DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://frontend:3000",
]


def get_cors_origins() -> list[str]:
    """Resolve allowed CORS origins.

    Reads the optional CORS_ORIGINS environment variable (comma-separated) and
    falls back to the explicit frontend origins (localhost:3000 variants) when
    it is not set.
    """
    origins_env = os.environ.get("CORS_ORIGINS")
    if origins_env:
        return [origin.strip() for origin in origins_env.split(",") if origin.strip()]
    return list(DEFAULT_CORS_ORIGINS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the Elasticsearch client lifecycle.

    Elasticsearch connections are opened per request via get_es_client() in the
    route layer, so no persistent client handle is stored here. This keeps the
    application startable in environments without a live Elasticsearch node
    (for example during unit testing).
    """
    yield


app = FastAPI(
    title="mesin-pencari-wisata-nusantara",
    description="Indonesian Tourism Vertical Search Engine REST API (Kelompok 10)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/", tags=["root"])
def root() -> dict:
    """Root endpoint with basic service information."""
    return {
        "app": "mesin-pencari-wisata-nusantara",
        "group": "Kelompok 10",
        "docs": "/docs",
    }
