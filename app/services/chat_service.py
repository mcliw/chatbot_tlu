from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, desc, func
from fastapi import HTTPException, status
from typing import Optional, List
import logging
from datetime import datetime

from app.models.chat import Conversation, Message
from app.models.user import User
from app.schemas.chat_schema import MessageCreate, MessageResponse, ConversationResponse
from app.shared.enums import ChatStatus, MessageType, UserRole
from app.sockets.manager import socket_manager

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, db: Session):
        self.db = db

    async def send_message(self, sender_id: str, data: MessageCreate) -> Message:
        """
        Gửi tin nhắn:
        1. Nếu chưa có conversation_id -> Tạo mới (Chỉ sinh viên được tạo)
        2. Lưu tin nhắn
        3. Cập nhật last_message_at của Conversation
        4. Emit sự kiện socket
        """
        try:
            conversation = None
            
            # 1. Xử lý Conversation
            if data.conversation_id:
                conversation = self.db.query(Conversation).filter(Conversation.id == data.conversation_id).first()
                if not conversation:
                    raise HTTPException(status_code=404, detail="Conversation not found")
            else:
                # Nếu không có ID, tạo mới (Logic cho Sinh viên bắt đầu chat)
                # Kiểm tra xem có hội thoại nào đang OPEN/PENDING không để reuse? (Tuỳ nghiệp vụ, ở đây tạo mới để đơn giản)
                conversation = Conversation(
                    student_id=sender_id,
                    status=ChatStatus.PENDING_AGENT, # Chờ Agent accept
                    title="Hỗ trợ sinh viên"
                )
                self.db.add(conversation)
                self.db.flush() # Để lấy ID

            # 2. Tạo Message
            new_msg = Message(
                conversation_id=conversation.id,
                sender_id=sender_id,
                content=data.content,
                msg_type=data.msg_type.value if data.msg_type else "TEXT"
            )
            self.db.add(new_msg)

            # 3. Update Conversation Metadata
            conversation.last_message_at = datetime.utcnow()
            
            # Nếu Chat đang CLOSED, user nhắn tin -> Reopen?
            if conversation.status == ChatStatus.CLOSED:
                conversation.status = ChatStatus.PENDING_AGENT

            self.db.commit()
            self.db.refresh(new_msg)

            # 4. Real-time Notification
            msg_data = MessageResponse.model_validate(new_msg).model_dump(mode='json')
            
            # Gửi cho room hội thoại (cho những người đang xem chat này)
            await socket_manager.emit_to_room(conversation.id, "new_message", msg_data)
            
            # Gửi thông báo cho Admin (nếu message từ sinh viên)
            if conversation.student_id == sender_id:
                # Logic thông báo cho Admin hoặc Agent đang phụ trách
                pass 

            return new_msg

        except Exception as e:
            self.db.rollback()
            logger.error(f"Send message error: {e}")
            raise HTTPException(status_code=500, detail="Failed to send message")

    def get_conversations(self, status_filter: Optional[ChatStatus], limit: int = 20) -> List[ConversationResponse]:
        """Lấy danh sách hội thoại cho Admin (Sort by last_message_at)"""
        query = self.db.query(Conversation)
        
        if status_filter:
            query = query.filter(Conversation.status == status_filter)
        
        conversations = query.order_by(desc(Conversation.last_message_at)).limit(limit).all()
        
        # Map sang schema (Có thể tối ưu bằng eager load tin nhắn cuối nếu cần)
        return [ConversationResponse.model_validate(c) for c in conversations]

    def get_messages(self, conversation_id: str, page: int, size: int) -> dict:
        """Lấy lịch sử tin nhắn (Phân trang)"""
        offset = (page - 1) * size
        total = self.db.query(Message).filter(Message.conversation_id == conversation_id).count()
        
        messages = self.db.query(Message)\
            .filter(Message.conversation_id == conversation_id)\
            .order_by(desc(Message.created_at))\
            .offset(offset).limit(size)\
            .all()
        
        # Đảo ngược lại để hiển thị đúng thứ tự thời gian (Cũ trên, Mới dưới) ở Client
        messages.reverse()
        
        return {
            "total": total,
            "items": [MessageResponse.model_validate(m) for m in messages]
        }

    async def assign_agent(self, conversation_id: str, agent_id: str) -> Conversation:
        """Gán Admin vào hỗ trợ"""
        conversation = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conversation.agent_id = agent_id
        conversation.status = ChatStatus.AGENT_PROCESSING
        self.db.commit()
        
        # Thông báo Socket
        await socket_manager.emit_to_room(conversation.id, "system_notification", {
            "content": "Agent has joined the chat",
            "type": "SYSTEM"
        })
        
        return conversation

    async def update_status(self, conversation_id: str, status: ChatStatus) -> Conversation:
        conversation = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conversation.status = status
        self.db.commit()
        
        # Thông báo
        await socket_manager.emit_to_room(conversation.id, "status_change", {"status": status.value})
        
        return conversation