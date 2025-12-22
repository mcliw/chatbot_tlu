# app/api/api_v1/routers/users.py
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.api.api_v1 import deps
from app.schemas.user_schema import StudentProfileResponse, UpdateProfileRequest
from app.services.student_service import StudentService
from app.models.user import User

router = APIRouter()

@router.get("/me", response_model=StudentProfileResponse)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Mobile: Lấy thông tin cá nhân (Profile) của user đang đăng nhập.
    """
    service = StudentService(db)
    return service.get_student_profile(current_user.id)

@router.put("/me", response_model=StudentProfileResponse)
async def update_user_me(
    # Các trường thông tin cá nhân (Optional)
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    
    # File Avatar (Optional) - Dùng File(None) để handle trường hợp không gửi file
    avatar: Optional[UploadFile] = File(None),
    
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Mobile: Cập nhật thông tin cá nhân và Avatar.
    Sử dụng Multipart/Form-Data.
    """
    # 1. Tạo DTO từ Form Data
    update_data = UpdateProfileRequest(phone=phone, address=address)
    
    # 2. Gọi Service xử lý (Service sẽ lo việc lưu file avatar nếu có)
    service = StudentService(db)
    return await service.update_profile(current_user.id, update_data, avatar)