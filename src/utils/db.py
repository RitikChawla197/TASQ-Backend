from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from src.utils.settings import settings


# Create the base class for models
Base = declarative_base()

# PostgreSQL connection URL from environment
DATABASE_URL = settings.resolved_database_url

engine_kwargs = {
    "pool_pre_ping": True,
    "pool_recycle": 3600,
    "echo": False,
}

if settings.should_use_null_pool:
    engine_kwargs["poolclass"] = NullPool

# Create the engine with connection pooling
engine = create_engine(DATABASE_URL, **engine_kwargs)

# Create the session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Dependency function to get database session
def get_db():
    """
    Dependency function to get a database session.
    Use this in FastAPI route handlers.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
