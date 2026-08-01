"""
Bharat Vanguard News (BVN) — FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse

from shared.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
)
logger = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # Initialize Sentry (if configured)
    if settings.sentry_dsn:
        import sentry_sdk
        sentry_sdk.init(dsn=settings.sentry_dsn, traces_sample_rate=0.1)
        logger.info("Sentry initialized")

    yield

    logger.info("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    description="AI-powered news intelligence platform API",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    default_response_class=ORJSONResponse,   # Faster JSON serialization
    lifespan=lifespan,
)

# ============================================================
#  MIDDLEWARE
# ============================================================

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ============================================================
#  ROUTERS
# ============================================================
from apps.api.routers import articles, events, publishers, entities, search, analytics, users, oauth  # noqa: E402

app.include_router(articles.router,    prefix="/api/v1/articles",    tags=["Articles"])
app.include_router(events.router,      prefix="/api/v1/events",      tags=["Events"])
app.include_router(publishers.router,  prefix="/api/v1/publishers",  tags=["Publishers"])
app.include_router(entities.router,    prefix="/api/v1/entities",    tags=["Entities"])
app.include_router(search.router,      prefix="/api/v1/search",      tags=["Search"])
app.include_router(analytics.router,   prefix="/api/v1/analytics",   tags=["Analytics"])
app.include_router(users.router,       prefix="/api/v1/users",       tags=["Users"])
app.include_router(oauth.router,       prefix="/api/v1/auth",        tags=["Auth / OAuth"])


# ============================================================
#  HEALTH CHECK
# ============================================================

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint — used by UptimeRobot to keep Render warm."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.app_env,
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }
