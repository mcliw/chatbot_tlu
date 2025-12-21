# app/models/chat.py
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, DateTime, Text, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.shared.enums import ChatStatus, MessageType

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Soft FK reference
    student_id: Mapped[str] = mapped_column(String(36), index=True)
    
    status: Mapped[ChatStatus] = mapped_column(Enum(ChatStatus), default=ChatStatus.OPEN)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    messages: Mapped[List["Message"]] = relationship("Message", back_populates="conversation",
                                                     primaryjoin="Conversation.id == foreign(Message.conversation_id)")

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    conversation_id: Mapped[str] = mapped_column(String(36), index=True)
    sender_id: Mapped[str] = mapped_column(String(36), index=True)
    
    content: Mapped[str] = mapped_column(Text)
    
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages",
                                                        primaryjoin="Message.conversation_id == foreign(Conversation.id)")