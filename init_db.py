from app.db.database import engine, Base
import app.models # Imports conversation, message, document, document_chunk, attachment
from sqlalchemy import text

print(f"Connecting to database (dialect: {engine.dialect.name})...")
try:
    if engine.dialect.name == "postgresql":
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            print("PostgreSQL pgvector extension verified.")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
except Exception as e:
    print(f"Database initialization error: {e}")

