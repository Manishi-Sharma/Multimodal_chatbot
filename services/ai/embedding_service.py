import os
import hashlib
import numpy as np
import logging
from google import genai
from google.genai import types
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        # Allow reusing LLM_API_KEY or GEMINI_API_KEY for embeddings
        self.api_key = settings.EMBEDDING_API_KEY or settings.LLM_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.model = settings.EMBEDDING_MODEL if settings.EMBEDDING_MODEL and settings.EMBEDDING_MODEL != "default-embedding" else "gemini-embedding-001"
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"GenAI Client init error in EmbeddingService: {e}")
                self.client = None
        else:
            self.client = None

    def generate_embedding(self, text: str) -> list[float]:
        if self.client:
            try:
                response = self.client.models.embed_content(
                    model=self.model,
                    contents=text,
                    config=types.EmbedContentConfig(output_dimensionality=768),
                )
                return response.embeddings[0].values
            except Exception as e:
                logger.warning(f"Error calling live embedding model: {e}. Falling back to deterministic vector.")

        # Deterministic pseudo-embedding for testing / offline mode
        # Preserves word matching similarity without requiring cloud API
        dim = 768
        vec = np.zeros(dim, dtype=np.float32)
        words = text.lower().split()
        for w in words:
            h = int(hashlib.md5(w.encode('utf-8')).hexdigest(), 16)
            idx = h % dim
            vec[idx] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        else:
            vec[0] = 1.0
        return vec.tolist()

embedding_service = EmbeddingService()

