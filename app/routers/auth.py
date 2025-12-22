# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.database.session import get_db
from app.services.auth_service import AuthService
from app.schemas.auth_schema import (
    LoginRequest, TokenResponse, StudentRegisterRequest, 
    LecturerCreateRequest, ChangePasswordRequest
)
from app.core.security import SECRET_KEY, ALGORITHM
from app.shared.enums import UserRole

router = APIRouter()

# Cấu hình Bearer Token cho Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login")

# --- DEPENDENCIES (Middleware) ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Giải mã token để lấy user hiện tại"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token không hợp lệ")
        return {"id": user_id, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token không hợp lệ hoặc đã hết hạn")

def verify_admin_role(current_user: dict = Depends(get_current_user)):
    """Middleware chỉ cho phép Admin"""
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Bạn không có quyền thực hiện chức năng này")
    return current_user

# --- ENDPOINTS ---

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """API Đăng nhập (Dùng chung cho Mobile & Web)"""
    return AuthService.authenticate_user(db, data)

@router.post("/register", status_code=201)
def register_student(data: StudentRegisterRequest, db: Session = Depends(get_db)):
    """API Đăng ký dành cho sinh viên (Mobile)"""
    new_user = AuthService.register_student(db, data)
    return {"message": "Đăng ký thành công", "email": new_user.email}

@router.post("/create-lecturer", status_code=201)
def create_lecturer(
    data: LecturerCreateRequest, 
    db: Session = Depends(get_db),
    admin_user: dict = Depends(verify_admin_role) # Chỉ Admin mới gọi được
):
    """API tạo giảng viên (Chỉ Admin trên Web Dashboard gọi)"""
    new_user = AuthService.create_lecturer_by_admin(db, data)
    return {"message": "Tạo giảng viên thành công", "email": new_user.email}

@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user) # Yêu cầu phải login
):
    """API Đổi mật khẩu"""
    return AuthService.change_password(db, current_user["id"], data.old_password, data.new_password)

@router.post("/forgot-password")
def forgot_password(email: str):
    # TODO: Tích hợp dịch vụ gửi email (như SendGrid/SMTP)
    # 1. Check email tồn tại
    # 2. Generate OTP/Link reset
    # 3. Gửi mail
    return {"message": "Nếu email tồn tại, hệ thống sẽ gửi hướng dẫn đặt lại mật khẩu."}