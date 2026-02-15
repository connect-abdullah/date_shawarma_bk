from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.logging import get_logger

logger = get_logger(__name__)

try:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_timeout=10,
        pool_recycle=1800,
        pool_pre_ping=True,
        connect_args={
            "connect_timeout": 5,
            "application_name": "date_shawarma_backend",
        },
        echo=False,
    )

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False
    )

    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        db.close()
