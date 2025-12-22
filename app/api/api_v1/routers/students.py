# app/api/api_v1/routers/students.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.api.api_v1 import deps
from app.schemas.user_schema import PaginatedStudentResponse, StudentProfileResponse
from app.services.student_service import StudentService
from app.shared.enums import AcademicStatus, UserRole
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=PaginatedStudentResponse)
def read_students(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    status: Optional[AcademicStatus] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser), # Chỉ Admin mới xem được
):
    """
    Web Admin: Danh sách sinh viên, filter, paging
    """
    service = StudentService(db)
    return service.get_students_list(page, size, keyword, status)

@router.get("/{user_id}", response_model=StudentProfileResponse)
def read_student_detail(
    user_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """
    Web Admin: Xem chi tiết sinh viên cụ thể (Lịch sử, GPA...)
    """
    service = StudentService(db)
    return service.get_student_profile(user_id)