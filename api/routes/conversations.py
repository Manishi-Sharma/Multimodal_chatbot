from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.conversation import ConversationRead, ConversationCreate, MessageRead
from typing import List
import uuid

router = APIRouter()

@router.get("/", response_model=List[ConversationRead])
def get_conversations(db: Session = Depends(get_db)):
    return db.query(Conversation).order_by(Conversation.updated_at.desc()).all()

@router.post("/", response_model=ConversationRead)
def create_conversation(conv: ConversationCreate, db: Session = Depends(get_db)):
    new_conv = Conversation(title=conv.title or "New Conversation")
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)
    return new_conv

@router.get("/{conversation_id}", response_model=ConversationRead)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()

@router.get("/{conversation_id}/messages", response_model=List[MessageRead])
def get_conversation_messages(conversation_id: str, db: Session = Depends(get_db)):
    return db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()

@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conv:
        db.delete(conv)
        db.commit()
    return {"status": "deleted"}
