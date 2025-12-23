from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

# Cấu hình mã hóa mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Cấu hình JWT
ALGORITHM = "HS256"
SECRET_KEY = settings.SECRET_KEY if hasattr(settings, "SECRET_KEY") else "YOUR_SUPER_SECRET_KEY_123"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Access token có hiệu lực 30 phút
REFRESH_TOKEN_EXPIRE_DAYS = 7  # Refresh token có hiệu lực 7 ngày

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """So sánh mật khẩu nhập vào và hash trong DB"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Mã hóa mật khẩu để lưu vào DB"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Tạo JWT Access Token chứa thông tin user (sub, role)"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Tạo JWT Refresh Token dùng để lấy access token mới"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> dict:
    """Xác minh và giải mã token, kiểm tra loại token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type_claim: str = payload.get("type")
        
        if user_id is None:
            return None
        
        if token_type_claim != token_type:
            return None
            
        return payload
    except JWTError:
        return None