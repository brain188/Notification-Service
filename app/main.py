import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncEngine
from app.api.v1.notifications import router as notifications_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import engine, SessionLocal
from app.workers.celery_app import celery_app
from app.metrics.prometheus import instrumentator

setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI(title="Notification Service API", version="1.0.0")

# CORS Middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # this will be adjusted in production for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

instrumentator.instrument(app).expose(app)


app.include_router(notifications_router, prefix="/api/v1")

# Dependency for DB session
async def get_db():
    async with SessionLocal() as session:
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Notification Service...")

    async with engine.begin() as conn:
        pass

    yield 

    logger.info("Shutting down Notification Service...")
    await engine.dispose()


# Root endpoint for health check
@app.get("/")
async def root():
    return {"message": "Notification Service is running"}