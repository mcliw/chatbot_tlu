from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from fastapi import HTTPException, UploadFile
from typing import Optional
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
        Lấy thông tin chi tiết (User + Student Info)
        """
        try:
            # Join bảng User và Student (nếu có)
            user = self.db.query(User).options(
                joinedload(User.student_profile)
            ).filter(User.id == user_id).first()

            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Lấy thông tin student (có thể None nếu user chưa có profile student)
            student_info = user.student_profile
            
            return StudentProfileResponse(
                user_id=user.id,
                full_name=user.full_name,
                email=user.email,
                avatar=user.avatar, # Cột avatar trong bảng users
                phone=user.phone,
                address=user.address,
                # Các trường từ bảng students (handle None an toàn)
                student_code=student_info.student_code if student_info else None,
                class_name=student_info.class_name if student_info else None,
                faculty=student_info.faculty if student_info else None,
                gpa=student_info.gpa if student_info else None,
                academic_status=student_info.academic_status if student_info else None,
                last_contact=student_info.last_contact if student_info else None
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Error fetching profile: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    async def update_profile(
        self, 
        user_id: str, 
        data: UpdateProfileRequest, 
        avatar_file: Optional[UploadFile]
    ) -> StudentProfileResponse:
        """
        Cập nhật Profile & Avatar.
        """
        # 1. Tìm user
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        try:
            # 2. Xử lý File Avatar (nếu client có gửi)
            if avatar_file:
                # Lưu file mới và lấy đường dẫn
                # Truyền user.avatar hiện tại vào để xóa file cũ
                new_avatar_path = await self.file_service.save_avatar(avatar_file, old_avatar_path=user.avatar)
                
                # Cập nhật đường dẫn vào DB
                user.avatar = new_avatar_path

            # 3. Cập nhật các thông tin text (chỉ update nếu có gửi lên)
            if data.phone is not None:
                user.phone = data.phone
            if data.address is not None:
                user.address = data.address

            # 4. Commit vào Database
            self.db.add(user)
            self.db.commit()
            
            # 5. Refresh để lấy data mới nhất từ DB (quan trọng)
            self.db.refresh(user)

            # 6. Trả về data profile mới nhất
            return self.get_student_profile(user_id)

        except HTTPException as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
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
            # Query cơ bản
            query = self.db.query(User).join(Student, User.id == Student.user_id).filter(User.role == UserRole.STUDENT)

            # Search keyword
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

            # Đếm tổng số & Phân trang
            total = query.count()
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