# app/services/student_service.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from fastapi import HTTPException, UploadFile
from typing import Optional, List
import logging

from app.models.user import User, Student
from app.schemas.user_schema import StudentProfileResponse, UpdateProfileRequest, PaginatedStudentResponse
from app.shared.enums import AcademicStatus, UserRole
from app.services.file_service import FileService

logger = logging.getLogger(__name__)

class StudentService:
    def __init__(self, db: Session):
        self.db = db
        self.file_service = FileService()

    def get_student_profile(self, user_id: str) -> StudentProfileResponse:
        """
        Lấy thông tin chi tiết (Join User + Student)
        Dùng Eager Loading (joinedload) để tối ưu query
        """
        try:
            user = self.db.query(User).options(
                joinedload(User.student_profile)
            ).filter(User.id == user_id).first()

            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Map dữ liệu sang Schema
            student_info = user.student_profile
            
            return StudentProfileResponse(
                user_id=user.id,
                full_name=user.full_name,
                email=user.email,
                avatar=user.avatar,
                phone=user.phone,
                address=user.address,
                student_code=student_info.student_code if student_info else None,
                class_name=student_info.class_name if student_info else None,
                faculty=student_info.faculty if student_info else None,
                gpa=student_info.gpa if student_info else None,
                academic_status=student_info.academic_status if student_info else None,
                last_contact=student_info.last_contact if student_info else None
            )
        except Exception as e:
            logger.error(f"Error fetching profile: {e}")
            raise e

    async def update_profile(self, user_id: str, data: UpdateProfileRequest, avatar_file: Optional[UploadFile]) -> StudentProfileResponse:
        """
        Cập nhật Profile & Avatar.
        Sử dụng Transaction thủ công để đảm bảo tính toàn vẹn.
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # 1. Xử lý File (nếu có)
            if avatar_file:
                # Lưu file mới, xóa file cũ, nhận đường dẫn mới
                new_avatar_path = await self.file_service.save_avatar(avatar_file, user.avatar)
                user.avatar = new_avatar_path

            # 2. Cập nhật thông tin text
            if data.phone is not None:
                user.phone = data.phone
            if data.address is not None:
                user.address = data.address

            # 3. Commit Transaction
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user) # Reload data sau khi commit

            return self.get_student_profile(user_id)

        except Exception as e:
            self.db.rollback() # Rollback DB nếu lỗi
            logger.error(f"Error updating profile for user {user_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to update profile")

    def get_students_list(
        self, 
        page: int, 
        size: int, 
        keyword: Optional[str], 
        status: Optional[AcademicStatus]
    ) -> PaginatedStudentResponse:
        """
        API cho Admin: List, Search, Filter, Pagination
        """
        try:
            # Query cơ bản join 2 bảng
            query = self.db.query(User).join(Student, User.id == Student.user_id).filter(User.role == UserRole.STUDENT)

            # Defensive programming: Handle keyword
            if keyword:
                search = f"%{keyword}%"
                query = query.filter(
                    or_(
                        User.full_name.ilike(search),
                        Student.student_code.ilike(search),
                        User.email.ilike(search)
                    )
                )

            # Filter Status
            if status:
                query = query.filter(Student.academic_status == status)

            # Đếm tổng số records
            total = query.count()

            # Phân trang
            users = query.offset((page - 1) * size).limit(size).all()

            # Mapping response
            items = []
            for u in users:
                s = u.student_profile
                items.append(StudentProfileResponse(
                    user_id=u.id,
                    full_name=u.full_name,
                    email=u.email,
                    avatar=u.avatar,
                    phone=u.phone,
                    address=u.address,
                    student_code=s.student_code,
                    class_name=s.class_name,
                    faculty=s.faculty,
                    gpa=s.gpa,
                    academic_status=s.academic_status,
                    last_contact=s.last_contact
                ))

            return PaginatedStudentResponse(
                total=total,
                page=page,
                size=size,
                items=items
            )

        except Exception as e:
            logger.error(f"Error fetching student list: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")