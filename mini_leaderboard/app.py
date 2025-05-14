from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from mini_leaderboard.config import get_config
from mini_leaderboard.dbutils import init_engine

from .routers.api.v1 import routers as v1_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = get_config()
    async with init_engine(config):
        yield


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow only the specified origins
    allow_credentials=True,  # Allow credentials (e.g., cookies, Authorization headers)
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


@app.middleware("http")
async def verify_token(request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)

    if request.url.path == "/" or request.url.path == "/docs" or request.url.path == "/openapi.json":
        return await call_next(request)
    config = get_config()
    if not config.api_token:
        # No auth
        return await call_next(request)
    if request.headers.get("Authorization") == f"Bearer {config.api_token}":
        return await call_next(request)

    return Response(
        status_code=401,
        content="Unauthorized. Check environment API_TOKEN for authentication.",
    )


@app.get("/")
async def hello():
    return {"message": "Hello World"}


for router in v1_routers:
    app.include_router(router)
