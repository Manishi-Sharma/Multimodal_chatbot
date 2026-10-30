from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.documents.parser import parser
from app.services.rag.chunker import chunker
from app.services.ai.embedding_service import embedding_service
from app.db.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

def process_document(document_id: str, file_path: str):
    db: Session = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            logger.error(f"Document {document_id} not found for processing.")
            return

        doc.processing_status = "processing"
        db.commit()

        # 1. Parse
        text = parser.parse(file_path, doc.file_type)

        # 2. Chunk
        chunks = chunker.chunk_text(text)

        # 3. Embed & Save
        for i, chunk_text in enumerate(chunks):
            embedding = embedding_service.generate_embedding(chunk_text)
            
            chunk_record = DocumentChunk(
                document_id=doc.id,
                chunk_index=i,
                content=chunk_text,
                embedding=embedding
            )
            db.add(chunk_record)

        doc.processing_status = "completed"
        db.commit()
        logger.info(f"Document {document_id} processed successfully.")

    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        db.rollback()
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.processing_status = "failed"
            db.commit()
    finally:
        db.close()
