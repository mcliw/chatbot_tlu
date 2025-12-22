from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text
from app.core.config import Settings
from app.database.session import engine, SessionLocal
from app.database.base import Base
from app.api.api_v1.api import api_router
import app.models
from fastapi.staticfiles import StaticFiles
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("⏳ Đang khởi tạo và kết nối Database...")
    
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Đã tạo cấu trúc bảng (Schema) thành công!")
        
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
            print("✅ Kết nối Database (Ping) thành công!")
            
    except Exception as e:
        print(f"❌ Lỗi nghiêm trọng khi kết nối DB: {e}")
    
    yield
    print("🛑 Server đang tắt...")

app = FastAPI(title="TLU Database Init", lifespan=lifespan)

@app.get("/")
def health_check():
    return {"message": "Database is ready!", "status": "connected"}

# Include API router
settings = Settings()
app.include_router(api_router, prefix=settings.API_V1_STR)

#Static files setup
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")