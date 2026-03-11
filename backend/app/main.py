import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin import router as admin_router
from app.api.auth import router as auth_router
from app.api.briefs import router as briefs_router
from app.api.entities import router as entities_router
from app.api.ios import router as ios_router
from app.api.search import router as search_router
from app.api.votes import router as votes_router
from app.config import settings

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)

app = FastAPI(
    title="Signal.ch API",
    description="The Swiss Intelligence Layer for News",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth_router, prefix="/v1")
app.include_router(ios_router, prefix="/v1")
app.include_router(entities_router, prefix="/v1")
app.include_router(search_router, prefix="/v1")
app.include_router(votes_router, prefix="/v1")
app.include_router(briefs_router, prefix="/v1")
app.include_router(admin_router, prefix="/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "signal-api"}


@app.get("/")
async def root():
    return {
        "name": "Signal.ch API",
        "version": "0.1.0",
        "docs": "/docs",
    }
