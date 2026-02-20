"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
import os

# Database URLs from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://farmsense_user:changeme@localhost:5432/farmsense"
)

TIMESCALE_URL = os.getenv(
    "TIMESCALE_URL",
    "postgresql://timescale_user:changeme@localhost:5433/farmsense_timeseries"
)

# SQLAlchemy engine configuration
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=False           # Set True for SQL logging
)

# TimescaleDB engine for time-series data
timescale_engine = create_engine(
    TIMESCALE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False
)

# Session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
TimescaleSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=timescale_engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions
    
    Usage:
        @app.get("/endpoint")
        async def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_map_db() -> Generator[Session, None, None]:
    """Database dependency for Map/Tile data"""
    db = MapSessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    from sqlalchemy import text
    from app.models import sensor_data
    
    # Create all tables
    sensor_data.Base.metadata.create_all(bind=engine)
    
    # Create PostGIS extension
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))
        conn.commit()
    
    print("Database initialized successfully")


if __name__ == "__main__":
    init_db()
