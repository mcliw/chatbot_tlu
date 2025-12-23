import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, DateTime, Text, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign
from app.database.base import Base
from app.shared.enums import ChatStatus

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # User ID của sinh viên (Soft FK)
    student_id: Mapped[str] = mapped_column(String(36), index=True)
    
    # User ID của Admin/Agent hỗ trợ (Soft FK)
    agent_id: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    
    # Thời gian tin nhắn cuối cùng để sort
    last_message_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    status: Mapped[ChatStatus] = mapped_column(Enum(ChatStatus), default=ChatStatus.OPEN)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    messages: Mapped[List["Message"]] = relationship(
        "Message", 
        back_populates="conversation",
        primaryjoin="Conversation.id == foreign(Message.conversation_id)",
        order_by="Message.created_at"
    )

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    conversation_id: Mapped[str] = mapped_column(String(36), index=True)
    sender_id: Mapped[str] = mapped_column(String(36), index=True)
    
    # Nội dung tin nhắn hoặc URL ảnh/file
    content: Mapped[str] = mapped_column(Text)
    
    # Loại tin nhắn: TEXT, IMAGE, FILE...
    msg_type: Mapped[str] = mapped_column(String(20), default="TEXT")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversation: Mapped["Conversation"] = relationship(
        "Conversation", 
        back_populates="messages",
        primaryjoin="foreign(Message.conversation_id) == Conversation.id"
    )