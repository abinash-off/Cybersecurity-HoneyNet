import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.api.auth import router as auth_router
from app.api.routes import router as api_router
from app.api.ws import router as ws_router
from app.config import get_settings
from app.database import Base, engine
from app.workers import start_workers, stop_workers

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("honeynet")

settings = get_settings()
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.api_rate_limit])


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Path("data").mkdir(parents=True, exist_ok=True)
    try:
        Path("/data").mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    Base.metadata.create_all(bind=engine)
    logger.info("HoneyNet Live starting data_mode=%s", settings.data_mode)
    start_workers()
    yield
    stop_workers()


app = FastAPI(
    title="HoneyNet Live API",
    description="Authorized research honeypot telemetry API. Admin routes require JWT.",
    version="1.0.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(api_router)
app.include_router(ws_router)


@app.get("/")
def root():
    return {"project": "HoneyNet Live", "docs": "/docs", "health": "/api/health"}


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response
