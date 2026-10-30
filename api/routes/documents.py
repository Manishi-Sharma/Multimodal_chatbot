from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentRead
from app.core.config import settings
from typing import List
import os
import shutil
import uuid
from app.services.documents.document_service import process_document

router = APIRouter()

def process_document_background(document_id: str, file_path: str):
    process_document(document_id, file_path)

@router.post("/upload", response_model=DocumentRead)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    # Validate file type (basic)
    allowed_types = ["application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/markdown"]
    if file.content_type not in allowed_types and not file.filename.endswith(('.pdf', '.txt', '.docx', '.md')):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Check file size (rough check via headers, proper check would read chunks)
    # Fastapi handles upload limits via server config mostly, but we can check here later.

    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    doc = Document(
        filename=file.filename,
        file_type=file.content_type or file_ext,
        file_path=file_path,
        processing_status="pending"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Schedule background processing
    background_tasks.add_task(process_document_background, doc.id, file_path)

    return doc

@router.get("/", response_model=List[DocumentRead])
def get_documents(db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.created_at.desc()).all()

@router.get("/{document_id}", response_model=DocumentRead)
def get_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.delete("/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if doc:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
        db.delete(doc)
        db.commit()
    return {"status": "deleted"}
