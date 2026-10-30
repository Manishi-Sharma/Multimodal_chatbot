from pydantic import BaseModel
from datetime import datetime

class DocumentRead(BaseModel):
    id: str
    filename: str
    file_type: str
    processing_status: str
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
