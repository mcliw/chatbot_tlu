# app/sockets/events.py
import socketio
import logging
from typing import Any

from app.sockets.manager import sio
from app.database.session import SessionLocal
from app.services.chat_service import ChatService
from app.schemas.chat_schema import MessageCreate
# Nếu cần verify token
# from app.core.security import verify_password, ALGORITHM, SECRET_KEY
# from jose import jwt

logger = logging.getLogger(__name__)

@sio.on("connect")
async def connect(sid, environ, auth):
    """
    Sự kiện khi Client kết nối.
    Auth có thể nằm trong packet handshake.
    """
    logger.info(f"Socket connected: {sid}")
    # TODO: Thực hiện verify token ở đây nếu cần bảo mật chặt chẽ
    # token = auth.get("token") if auth else None
    # if not token: raise ConnectionRefusedError("No token provided")

@sio.on("disconnect")
async def disconnect(sid):
    logger.info(f"Socket disconnected: {sid}")

@sio.on("join_room")
async def handle_join_room(sid, data):
    """
    Client gửi yêu cầu tham gia phòng chat.
    Data format: {"room_id": "conversation_id"}
    """
    room_id = data.get("room_id")
    if room_id:
        # --- FIX LỖI TẠI ĐÂY ---
        # Thêm 'await' vì enter_room là hàm bất đồng bộ trong AsyncServer
        await sio.enter_room(sid, room_id)
        
        logger.info(f"SID {sid} joined room {room_id}")
        
        # Gửi thông báo cho mọi người trong room biết
        await sio.emit("system_notification", {"content": "User joined room"}, room=room_id)

@sio.on("send_message")
async def handle_send_message(sid, data):
    """
    Nhận tin nhắn từ Client -> Lưu DB -> Broadcast lại
    Data: {"conversation_id": "...", "content": "...", "sender_id": "...", "msg_type": "TEXT"}
    """
    db = SessionLocal()
    try:
        service = ChatService(db)
        
        conversation_id = data.get("conversation_id")
        content = data.get("content")
        
        # Validate input cơ bản
        if not conversation_id and not content:
            return

        # Tạo DTO
        msg_dto = MessageCreate(
            conversation_id=conversation_id,
            content=content,
            msg_type=data.get("msg_type", "TEXT") # Lấy msg_type từ client gửi lên
        )
        sender_id = data.get("sender_id") 

        # Gọi Service xử lý (Lưu DB + Emit socket trong service)
        # Lưu ý: Hàm send_message trong ChatService phải là async def để dùng await
        await service.send_message(sender_id, msg_dto)
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await sio.emit("error", {"detail": str(e)}, to=sid)
    finally:
        db.close()

@sio.on("typing")
async def handle_typing(sid, data):
    """
    Hiển thị trạng thái 'Đang nhập...'
    Data: {"room_id": "...", "is_typing": true}
    """
    room_id = data.get("room_id")
    if room_id:
        # Broadcast cho những người khác trong room (skip_sid=sid để không gửi lại cho chính mình)
        await sio.emit("typing", data, room=room_id, skip_sid=sid)