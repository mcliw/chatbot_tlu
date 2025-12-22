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
    Mobile: Lấy thông tin cá nhân của user đang đăng nhập
    """
    service = StudentService(db)
    return service.get_student_profile(current_user.id)

@router.put("/me", response_model=StudentProfileResponse)
async def update_user_me(
    # Sử dụng Optional[...] = Form(None) để FastAPI hiểu rằng trường này có thể không được gửi lên
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    # Sử dụng Optional[UploadFile] = File(None) để xử lý trường hợp user không chọn ảnh mới
    avatar: Optional[UploadFile] = File(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Mobile: Cập nhật Profile.
    Dùng Form Data để hỗ trợ upload file cùng lúc.
    """
    # Convert Form data sang Pydantic model để validate logic nghiệp vụ
    update_data = UpdateProfileRequest(phone=phone, address=address)
    
    service = StudentService(db)
    return await service.update_profile(current_user.id, update_data, avatar)