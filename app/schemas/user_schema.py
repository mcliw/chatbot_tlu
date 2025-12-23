from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from app.shared.enums import UserRole, AcademicStatus

# --- BASE ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: bool = True
    role: UserRole

class StudentBase(BaseModel):
    student_code: str
    class_name: str
    faculty: str
    gpa: Optional[float] = None
    academic_status: AcademicStatus

# --- RESPONSES ---
class StudentProfileResponse(BaseModel):
    """Dùng cho Mobile xem Profile & Admin xem chi tiết"""
    user_id: str
    full_name: str
    email: str
    avatar: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    
    # Thông tin sinh viên
    student_code: Optional[str] = None
    class_name: Optional[str] = None
    faculty: Optional[str] = None
    gpa: Optional[float] = None
    academic_status: Optional[AcademicStatus] = None
    last_contact: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class PaginatedStudentResponse(BaseModel):
    """Dùng cho Admin List"""
    total: int
    page: int
    size: int
    items: List[StudentProfileResponse]

# --- REQUESTS ---
class UpdateProfileRequest(BaseModel):
    """Mobile cập nhật thông tin"""
    phone: Optional[str] = Field(None, max_length=15, pattern=r"^\+?[0-9]*$")
    address: Optional[str] = Field(None, max_length=255)
    # Avatar sẽ được gửi qua Multipart Form Data, không nằm trong JSON body này