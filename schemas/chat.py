from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    conversation_id: str
    message: str
    attachments: Optional[List[str]] = []
    web_search: bool = False

class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    content: str
    role: str = "assistant"
    sources: Optional[List[dict]] = []

