# app/sockets/manager.py
import socketio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Khởi tạo Socket.IO Server (Async)
# cors_allowed_origins='*' để dev, production nên config cụ thể
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

class SocketManager:
    """Helper class để quản lý rooms và events"""
    
    @staticmethod
    async def emit_to_room(room: str, event: str, data: dict):
        try:
            await sio.emit(event, data, room=room)
        except Exception as e:
            logger.error(f"Socket emit error: {e}")

    @staticmethod
    async def emit_to_user(user_id: str, event: str, data: dict):
        """Gửi event đến room cá nhân của user"""
        try:
            await sio.emit(event, data, room=f"user_{user_id}")
        except Exception as e:
            logger.error(f"Socket emit user error: {e}")

socket_manager = SocketManager()