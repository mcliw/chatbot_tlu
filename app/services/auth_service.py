# app/services/auth_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, Student, Agent
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.auth_schema import StudentRegisterRequest, LecturerCreateRequest, LoginRequest
from app.shared.enums import UserRole, AcademicStatus

class AuthService:
    
    @staticmethod
    def authenticate_user(db: Session, login_data: LoginRequest):
        """Xử lý đăng nhập và cấp token"""
        # 1. Tìm user theo email
        user = db.query(User).filter(User.email == login_data.email).first()
        if not user:
            raise HTTPException(status_code=400, detail="Email hoặc mật khẩu không chính xác")
        
        # 2. Kiểm tra mật khẩu
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(status_code=400, detail="Email hoặc mật khẩu không chính xác")
        
        # 3. Kiểm tra active
        if not user.is_active:
             raise HTTPException(status_code=400, detail="Tài khoản đã bị khóa")

        # 4. Tạo token
        access_token = create_access_token(data={"sub": user.id, "role": user.role.value})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": user.role.value,
            "user_id": user.id,
            "full_name": user.full_name
        }

    @staticmethod
    def register_student(db: Session, data: StudentRegisterRequest):
        """Đăng ký tài khoản Sinh viên (Mặc định Role STUDENT)"""
        # 1. Check email tồn tại
        if db.query(User).filter(User.email == data.email).first():
            raise HTTPException(status_code=400, detail="Email đã được sử dụng")
        
        # 2. Check mã sinh viên tồn tại
        if db.query(Student).filter(Student.student_code == data.student_code).first():
            raise HTTPException(status_code=400, detail="Mã sinh viên đã tồn tại")

        try:
            # 3. Tạo User Record
            new_user = User(
                email=data.email,
                password_hash=get_password_hash(data.password),
                full_name=data.full_name,
                role=UserRole.STUDENT, # Mặc định là Student
                is_active=True
            )
            db.add(new_user)
            db.flush() # Để lấy user.id

            # 4. Tạo Student Record (Soft FK)
            new_student = Student(
                user_id=new_user.id, # Link với user vừa tạo
                student_code=data.student_code,
                class_name=data.class_name,
                faculty=data.faculty,
                academic_status=AcademicStatus.ACTIVE
            )
            db.add(new_student)
            db.commit()
            db.refresh(new_user)
            return new_user
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")

    @staticmethod
    def create_lecturer_by_admin(db: Session, data: LecturerCreateRequest):
        """Admin tạo tài khoản Giảng viên (Role LECTURER)"""
        if db.query(User).filter(User.email == data.email).first():
            raise HTTPException(status_code=400, detail="Email đã tồn tại")

        try:
            # 1. Tạo User
            new_user = User(
                email=data.email,
                password_hash=get_password_hash(data.password),
                full_name=data.full_name,
                role=UserRole.LECTURER, # Gán cứng role Lecturer
                is_active=True
            )
            db.add(new_user)
            db.flush()

            # 2. Tạo Agent (Giảng viên/Admin profile)
            new_agent = Agent(
                user_id=new_user.id,
                department=data.department,
                status="OFFLINE"
            )
            db.add(new_agent)
            db.commit()
            return new_user
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def change_password(db: Session, user_id: str, old_pass: str, new_pass: str):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not verify_password(old_pass, user.password_hash):
            raise HTTPException(status_code=400, detail="Mật khẩu cũ không đúng")
            
        user.password_hash = get_password_hash(new_pass)
        db.commit()
        return {"message": "Đổi mật khẩu thành công"}