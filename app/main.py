import os
from contextlib import asynccontextmanager

import socketio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

# Import Config & Database
from app.core.config import Settings
from app.database.session import engine, SessionLocal
from app.database.base import Base
from app.api.api_v1.api import api_router
import app.models  # Import models để SQLAlchemy nhận diện được các bảng khi create_all

# Import Socket
from app.sockets.manager import sio
from app.sockets import events  # QUAN TRỌNG: Import để đăng ký các sự kiện @sio.on

# Khởi tạo Settings
settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Quản lý vòng đời ứng dụng:
    1. Khởi tạo Database Tables (nếu chưa có).
    2. Kiểm tra kết nối DB.
    """
    print("⏳ Đang khởi tạo và kết nối Database...")
    
    try:
        # Tạo bảng dựa trên metadata của Base
        Base.metadata.create_all(bind=engine)
        print("✅ Đã tạo cấu trúc bảng (Schema) thành công!")
        
        # Thử kết nối DB
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
            print("✅ Kết nối Database (Ping) thành công!")
            
    except Exception as e:
        print(f"❌ Lỗi nghiêm trọng khi kết nối DB: {e}")
    
    yield
    print("🛑 Server đang tắt...")

# Khởi tạo FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME if hasattr(settings, 'PROJECT_NAME') else "TLU Chatbot API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# --- CẤU HÌNH CORS (Bắt buộc cho Web/Mobile Client & Socket) ---
# Nếu settings có cấu hình CORS, sử dụng nó. Nếu không, cho phép tất cả (môi trường dev).
if hasattr(settings, 'BACKEND_CORS_ORIGINS') and settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Fallback cho môi trường dev nếu chưa config trong .env
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/")
def health_check():
    return {"message": "Database is ready!", "status": "connected"}

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

# --- CẤU HÌNH STATIC FILES ---
# Tạo thư mục static nếu chưa tồn tại
if not os.path.exists("static"):
    os.makedirs("static")

# Mount thư mục static để phục vụ file ảnh/upload
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- TÍCH HỢP SOCKET.IO ---
# Wrap FastAPI app bằng SocketIO ASGIApp
# Mọi request đến /socket.io sẽ được xử lý bởi sio, các request khác chuyển cho app FastAPI
app = socketio.ASGIApp(
    socketio_server=sio,
    other_asgi_app=app,
    socketio_path='/socket.io'
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)