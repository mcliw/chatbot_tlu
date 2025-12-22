# app/models/user.py
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, Integer, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.shared.enums import UserRole, AcademicStatus 

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.STUDENT)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True) # Bổ sung trường is_active mà AuthService cần dùng
    
    # --- QUAN HỆ (RELATIONSHIPS) ---
    # Quan hệ với bảng Student
    student_profile: Mapped["Student"] = relationship("Student", back_populates="user", uselist=False, 
                                                      primaryjoin="User.id == foreign(Student.user_id)")
    
    # Quan hệ với bảng Agent (Admin/Giảng viên)
    agent_profile: Mapped["Agent"] = relationship("Agent", back_populates="user", uselist=False,
                                                  primaryjoin="User.id == foreign(Agent.user_id)")

class Student(Base):
    __tablename__ = "students"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Soft FK
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    
    student_code: Mapped[str] = mapped_column(String(20), unique=True)
    class_name: Mapped[str] = mapped_column(String(50))
    faculty: Mapped[str] = mapped_column(String(100)) # Bổ sung trường faculty
    gpa: Mapped[float] = mapped_column(Integer, nullable=True)
    academic_status: Mapped[AcademicStatus] = mapped_column(Enum(AcademicStatus), default=AcademicStatus.ACTIVE)

    user: Mapped["User"] = relationship("User", back_populates="student_profile", 
                                        primaryjoin="Student.user_id == foreign(User.id)")

class Agent(Base):
    """Bảng giảng viên/admin"""
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Soft FK
    user_id: Mapped[str] = mapped_column(String(36), index=True)

    department: Mapped[str] = mapped_column(String(100)) # Phòng đào tạo, Khoa CNTT...
    status: Mapped[str] = mapped_column(String(50), default="OFFLINE") # ONLINE, BUSY...

    user: Mapped["User"] = relationship("User", back_populates="agent_profile",
                                        primaryjoin="Agent.user_id == foreign(User.id)")