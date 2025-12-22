# app/api/api_v1/deps.py
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.database.session import SessionLocal
from app.models.user import User
from app.shared.enums import UserRole

# Khởi tạo settings
settings = Settings()

# Cấu hình OAuth2: Token Url phải khớp với router auth
# Giả sử trong auth.py route login là /login/access-token
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/access-token"
)

def get_db() -> Generator:
    """Dependency để lấy DB Session"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    """Giải mã token và lấy User hiện tại"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = payload.get("sub")
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    # Lấy user từ DB dựa trên email hoặc ID (tùy vào cách bạn gen token ở auth.py)
    # Ở đây giả sử "sub" chứa user_id. Nếu "sub" chứa email thì đổi thành filter(User.email == token_data)
    user = db.query(User).filter(User.id == token_data).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Kiểm tra user có đang active không"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_active_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Chỉ cho phép Admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user