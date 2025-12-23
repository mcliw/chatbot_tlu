from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.shared.enums import UserRole

# Schema cho Login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Schema phản hồi Token sau khi Login
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    role: str
    user_id: str
    full_name: str

# Schema request để refresh token
class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Schema phản hồi khi verify auth token
class AuthTokenResponse(BaseModel):
    user_id: str
    role: str
    is_valid: bool
    message: str

# Schema Đăng ký sinh viên (Public)
class StudentRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    student_code: str
    class_name: str
    faculty: str

# Schema Tạo Giảng viên (Admin only)
class LecturerCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    department: str

# Schema Đổi mật khẩu
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)