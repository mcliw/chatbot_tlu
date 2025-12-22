# app/models/user.py
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, Enum, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign
from app.database.base import Base
from app.shared.enums import UserRole, AcademicStatus 

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.STUDENT)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # --- THÊM MỚI (UPDATE PROFILE MOBILE) ---
    avatar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True) # URL ảnh
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # --- QUAN HỆ ---
    student_profile: Mapped["Student"] = relationship(
        "Student", 
        back_populates="user", 
        uselist=False, 
        primaryjoin="User.id == foreign(Student.user_id)"
    )
    
    agent_profile: Mapped["Agent"] = relationship(
        "Agent", 
        back_populates="user", 
        uselist=False,
        primaryjoin="User.id == foreign(Agent.user_id)"
    )

class Student(Base):
    __tablename__ = "students"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    
    student_code: Mapped[str] = mapped_column(String(20), unique=True)
    class_name: Mapped[str] = mapped_column(String(50))
    faculty: Mapped[str] = mapped_column(String(100))
    
    # CẬP NHẬT: Integer -> Float cho GPA
    gpa: Mapped[float] = mapped_column(Float, nullable=True) 
    academic_status: Mapped[AcademicStatus] = mapped_column(Enum(AcademicStatus), default=AcademicStatus.ACTIVE)

    # --- THÊM MỚI (CHO WEB ADMIN DASHBOARD) ---
    last_contact: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    total_chats: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["User"] = relationship(
        "User", 
        back_populates="student_profile", 
        primaryjoin="foreign(Student.user_id) == User.id"
    )

class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    department: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default="OFFLINE")

    user: Mapped["User"] = relationship(
        "User", 
        back_populates="agent_profile",
        primaryjoin="foreign(Agent.user_id) == User.id"
    )