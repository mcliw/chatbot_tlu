# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from config import settings

# Cấu hình mã hóa mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Cấu hình JWT
ALGORITHM = "HS256"
# Lưu ý: Nên đưa SECRET_KEY vào .env (settings)
SECRET_KEY = settings.SECRET_KEY if hasattr(settings, "SECRET_KEY") else "YOUR_SUPER_SECRET_KEY_123"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 ngày

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """So sánh mật khẩu nhập vào và hash trong DB"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Mã hóa mật khẩu để lưu vào DB"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Tạo JWT Token chứa thông tin user (sub, role)"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt