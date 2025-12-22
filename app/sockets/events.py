# app/sockets/events.py
from typing import Any
import socketio
from app.sockets.manager import sio
from app.database.session import SessionLocal
from app.services.chat_service import ChatService
from app.schemas.chat_schema import MessageCreate
from app.shared.enums import MessageType
from app.core.security import verify_password, ALGORITHM, SECRET_KEY
from jose import jwt

# Middleware xác thực (Tùy chọn: Token thường gửi qua query param hoặc headers handshake)
@sio.on("connect")
async def connect(sid, environ, auth):
    # Lấy token từ auth payload hoặc query params
    # Ví dụ đơn giản: auth={'token': '...'}
    print(f"Socket connected: {sid}")
    # Có thể verify token ở đây, nếu fail -> raise ConnectionRefusedError

@sio.on("disconnect")
async def disconnect(sid):
    print(f"Socket disconnected: {sid}")

@sio.on("join_room")
async def handle_join_room(sid, data):
    """
    Data format: {"room_id": "conversation_id"} hoặc {"user_id": "..."}
    """
    room_id = data.get("room_id")
    if room_id:
        sio.enter_room(sid, room_id)
        print(f"SID {sid} joined room {room_id}")
        await sio.emit("system_notification", {"content": "User joined room"}, room=room_id)

@sio.on("send_message")
async def handle_send_message(sid, data):
    """
    Nhận tin nhắn từ Client -> Lưu DB -> Broadcast lại
    Data: {"conversation_id": "...", "content": "...", "sender_id": "...", "type": "TEXT"}
    """
    db = SessionLocal()
    try:
        service = ChatService(db)
        
        # Validate & Create DTO
        msg_dto = MessageCreate(
            conversation_id=data.get("conversation_id"),
            content=data.get("content"),
            msg_type=data.get("type", "TEXT")
        )
        sender_id = data.get("sender_id") # Trong thực tế nên lấy từ Auth Token của Session

        # Gọi Service xử lý
        await service.send_message(sender_id, msg_dto)
        
        # (Lưu ý: Service đã handle việc emit "new_message" rồi)
        
    except Exception as e:
        print(f"Error handling message: {e}")
        await sio.emit("error", {"detail": str(e)}, to=sid)
    finally:
        db.close()

@sio.on("typing")
async def handle_typing(sid, data):
    """
    Data: {"room_id": "...", "is_typing": true, "user_name": "..."}
    """
    room_id = data.get("room_id")
    if room_id:
        # Broadcast cho những người khác trong room (skip_sid=sid)
        await sio.emit("typing", data, room=room_id, skip_sid=sid)