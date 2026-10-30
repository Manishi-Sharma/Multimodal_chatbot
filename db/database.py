import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

Base = declarative_base()

def get_engine():
    db_url = settings.DATABASE_URL
    try:
        # Test connecting to configured database
        eng = create_engine(db_url, pool_pre_ping=True)
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"Connected to database successfully: {db_url.split('@')[-1] if '@' in db_url else db_url}")
        return eng
    except Exception as e:
        logger.warning(
            f"Could not connect to configured DATABASE_URL ({e}). "
            "Falling back to local SQLite database: sqlite:///./multimodal_ai.db"
        )
        sqlite_url = "sqlite:///./multimodal_ai.db"
        return create_engine(sqlite_url, connect_args={"check_same_thread": False})

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

