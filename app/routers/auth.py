from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.database.session import get_db
from app.services.auth_service import AuthService
from app.schemas.auth_schema import (
    LoginRequest, TokenResponse, StudentRegisterRequest, 
    LecturerCreateRequest, ChangePasswordRequest, RefreshTokenRequest, AuthTokenResponse
)
from app.core.security import SECRET_KEY, ALGORITHM, verify_token
from app.shared.enums import UserRole

router = APIRouter()

# Cấu hình Bearer Token cho Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login")

# --- DEPENDENCIES (Middleware) ---
def authenticateToken(token: str = Depends(oauth2_scheme)):
    """Middleware xác thực token (kiểm tra token có hợp lệ không)"""
    payload = verify_token(token, token_type="access")
    if payload is None:
        raise HTTPException(status_code=401, detail="Access token không hợp lệ hoặc đã hết hạn")
    return payload

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Giải mã access token để lấy user hiện tại"""
    payload = verify_token(token, token_type="access")
    if payload is None:
        raise HTTPException(status_code=401, detail="Access token không hợp lệ hoặc đã hết hạn")
    
    user_id: str = payload.get("sub")
    role: str = payload.get("role")
    return {"id": user_id, "role": role}

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

@router.get("/auth_token", response_model=AuthTokenResponse)
def verify_auth_token(payload: dict = Depends(authenticateToken), db: Session = Depends(get_db)):
    """API Xác minh token hợp lệ - kiểm tra token và trả về thông tin user"""
    user_id: str = payload.get("sub")
    user_role: str = payload.get("role")
    
    return AuthService.verify_auth_token(db, user_id, user_role)

@router.post("/refresh")
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """API Làm mới access token từ refresh token"""
    payload = verify_token(data.refresh_token, token_type="refresh")
    if payload is None:
        raise HTTPException(status_code=401, detail="Refresh token không hợp lệ hoặc đã hết hạn")
    
    user_id: str = payload.get("sub")
    role: str = payload.get("role")
    
    return AuthService.refresh_access_token(db, user_id, role)

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