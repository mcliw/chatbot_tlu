# app/schemas/chat_schema.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.shared.enums import ChatStatus, MessageType

# --- Message ---
class MessageCreate(BaseModel):
    conversation_id: Optional[str] = None # Nếu null -> tạo hội thoại mới (client gửi message đầu tiên)
    content: str
    msg_type: MessageType = MessageType.TEXT

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    sender_id: str
    content: str
    msg_type: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Conversation ---
class ConversationResponse(BaseModel):
    id: str
    student_id: str
    agent_id: Optional[str] = None
    title: Optional[str] = None
    status: ChatStatus
    created_at: datetime
    last_message_at: Optional[datetime] = None
    
    # Có thể include tin nhắn cuối cùng để hiển thị preview
    last_message: Optional[str] = None 

    model_config = ConfigDict(from_attributes=True)

class ConversationDetailResponse(ConversationResponse):
    messages: List[MessageResponse] = []

# --- Pagination ---
class PaginatedMessagesResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[MessageResponse]