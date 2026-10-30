from sqlalchemy.orm import Session
from app.models.document_chunk import DocumentChunk
from app.services.ai.embedding_service import embedding_service
from app.core.config import settings
import numpy as np
from typing import List, Optional

class RetrieverService:
    def retrieve_context(
        self, 
        query: str, 
        db: Session, 
        top_k: Optional[int] = None, 
        document_ids: Optional[List[str]] = None
    ) -> list[DocumentChunk]:
        k = top_k or settings.TOP_K
        query_embedding = embedding_service.generate_embedding(query)
        
        query_builder = db.query(DocumentChunk)
        if document_ids:
            query_builder = query_builder.filter(DocumentChunk.document_id.in_(document_ids))

        # Check if database dialect is PostgreSQL with pgvector
        if db.bind.dialect.name == "postgresql":
            results = query_builder.order_by(
                DocumentChunk.embedding.cosine_distance(query_embedding)
            ).limit(k).all()
            return results
        else:
            # SQLite fallback: calculate cosine similarity using numpy
            chunks = query_builder.all()
            if not chunks:
                return []
                
            q_vec = np.array(query_embedding, dtype=np.float32)
            norm_q = np.linalg.norm(q_vec)
            if norm_q == 0:
                return chunks[:k]
                
            scored = []
            for c in chunks:
                if c.embedding:
                    c_vec = np.array(c.embedding, dtype=np.float32)
                    norm_c = np.linalg.norm(c_vec)
                    if norm_c > 0:
                        sim = float(np.dot(q_vec, c_vec) / (norm_q * norm_c))
                        scored.append((sim, c))
                        
            scored.sort(key=lambda x: x[0], reverse=True)
            return [chunk for _, chunk in scored[:k]]

retriever = RetrieverService()

