from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator
from pgvector.sqlalchemy import Vector
from app.db.database import Base
import json
import uuid

class CompatibleVector(TypeDecorator):
    """
    Dual-dialect vector type:
    Uses native pgvector Vector(dim) when on PostgreSQL,
    and JSON serialized Text when on SQLite.
    """
    impl = Text
    cache_ok = True

    def __init__(self, dim=768, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dim = dim

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(Vector(self.dim))
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return value
        return value

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    # Using 768 dimensions for typical embedding models (e.g. text-embedding-004)
    embedding = Column(CompatibleVector(768), nullable=True) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())

