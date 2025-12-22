# app/models/chat.py
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, DateTime, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign # Thêm foreign vào đây
from app.database.base import Base
from app.shared.enums import ChatStatus

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    student_id: Mapped[str] = mapped_column(String(36), index=True)
    status: Mapped[ChatStatus] = mapped_column(Enum(ChatStatus), default=ChatStatus.OPEN)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Đúng: foreign() bọc quanh cột tham chiếu ở bảng con
    messages: Mapped[List["Message"]] = relationship(
        "Message", 
        back_populates="conversation",
        primaryjoin="Conversation.id == foreign(Message.conversation_id)"
    )

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    conversation_id: Mapped[str] = mapped_column(String(36), index=True)
    sender_id: Mapped[str] = mapped_column(String(36), index=True)
    content: Mapped[str] = mapped_column(Text)
    
    # SỬA TẠI ĐÂY: foreign() phải bọc quanh Message.conversation_id
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", 
        back_populates="messages",
        primaryjoin="foreign(Message.conversation_id) == Conversation.id"
    )