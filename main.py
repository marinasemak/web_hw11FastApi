from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI, Depends, Request
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi.middleware.cors import CORSMiddleware

import logging
from config.general import settings
from src.users.routes import router as users_router
from src.auth.routes import router as auth_router
from src.contacts.routes import router as contacts_router
from src.contacts.routes import unexpected_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Hide description from Swagger
    openapi_schema = app.openapi()
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["description"] = None  # Видаляємо опис
    app.openapi_schema = openapi_schema

    # Connect to Redis
    redis_connection = await redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(redis_connection)
    try:
        yield
    finally:
        await redis_connection.close()


app = FastAPI(lifespan=lifespan)
logging.basicConfig(level=logging.INFO)
origins = ["http://localhost:3000"]


@app.on_event("startup")
def customize_openapi():
    openapi_schema = app.openapi()
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.pop("description", None)  # Прибираємо опис
    app.openapi_schema = openapi_schema


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Request from origin: {request.headers.get('origin')}")
    response = await call_next(request)
    return response


@app.get("/api/healthchecker", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def healthcheck():
    return {"message": "Welcome to FastAPI!"}


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(contacts_router, prefix="/contacts", tags=["contacts"])
app.add_exception_handler(Exception, unexpected_exception_handler)
