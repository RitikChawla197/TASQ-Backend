from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.utils.db import engine, Base, get_db
from src.utils.settings import settings
from src.tasks.router import task_routes
from src.users.router import user_routes
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.AUTO_CREATE_TABLES:
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Task Management Application", lifespan=lifespan)
app.include_router(task_routes)
app.include_router(user_routes)

origins = [origin.strip().rstrip("/") for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
allow_credentials = "*" not in origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/")
async def root():
    return {"message": "Task Management Application is running"}


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify database connection.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
