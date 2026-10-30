from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.orchestration.chat_orchestrator import chat_orchestrator
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    # Verify conversation exists or auto-create it
    conv = db.query(Conversation).filter(Conversation.id == request.conversation_id).first()
    if not conv:
        conv = Conversation(
            id=request.conversation_id, 
            title=request.message.strip()[:40] if request.message else "New Conversation"
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
        
    # Save user message
    user_msg = Message(
        conversation_id=request.conversation_id,
        role="user",
        content=request.message,
    )
    db.add(user_msg)
    
    # Generate AI response using orchestrator
    orchestration_result = chat_orchestrator.handle_request(
        user_message=request.message, 
        db=db, 
        conversation_id=request.conversation_id,
        attachments=request.attachments,
        use_web_search=request.web_search
    )
    ai_content = orchestration_result["content"]
    sources = orchestration_result.get("sources", [])
    
    # Save AI message
    ai_msg = Message(
        conversation_id=request.conversation_id,
        role="assistant",
        content=ai_content,
    )
    db.add(ai_msg)
    
    # Update conversation timestamp
    conv.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(ai_msg)
    
    return ChatResponse(
        conversation_id=request.conversation_id,
        message_id=ai_msg.id,
        content=ai_content,
        role="assistant",
        sources=sources
    )
