import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import time
import uuid
from contextlib import asynccontextmanager

import joblib
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.logging_config import logger
from app.routers import v1


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = joblib.load(settings.MODEL_PATH)
    logger.info(f"Model loaded successfully from {settings.MODEL_PATH}")
    yield
    logger.info("Shutting down. Model unloaded.")


app = FastAPI(title=settings.API_TITLE, lifespan=lifespan)
app.include_router(v1.router)


@app.get("/")
def root():
    return {"message": "ML API is alive"}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)

    logger.info(
        f"request_id={request_id} method={request.method} path={request.url.path} "
        f"status_code={response.status_code} duration_ms={duration_ms}"
    )
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"request_id={request_id} event=value_error error={exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid data encountered during prediction. Please check your input values."},
    )
