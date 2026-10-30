from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MessageBase(BaseModel):
    role: str
    content: str
    message_type: str = "text"

class MessageRead(MessageBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    title: Optional[str] = None

class ConversationCreate(ConversationBase):
    pass

class ConversationRead(ConversationBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
