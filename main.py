from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.db.database import engine, Base
import app.models  # Registers all models with Base.metadata
from app.api.routes import health, chat, conversations, documents
import logging

logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-initialize database tables on server start
    try:
        if engine.dialect.name == "postgresql":
            with engine.begin() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified and initialized successfully.")
    except Exception as e:
        logger.warning(f"Database initialization notice: {e}")
    yield

app = FastAPI(
    title="Multimodal AI Chatbot API",
    description="Production-ready FastAPI backend with RAG, Web Search, and Multimodal integration.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": "Multimodal AI Chatbot API",
        "database": engine.dialect.name,
        "docs_url": "/docs"
    }

