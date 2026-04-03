from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class MessageCreate(BaseModel):
    content: str


class MessageOut(BaseModel):
    id: str
    chat_id: str
    sender_id: str
    content: str
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatOut(BaseModel):
    id: str
    participants: List[str]
    service_request_id: str
    created_at: datetime
    updated_at: datetime
    last_message: Optional[MessageOut] = None
    unread_count: int = 0

    model_config = {"from_attributes": True}
