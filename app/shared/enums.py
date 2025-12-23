from enum import Enum

class UserRole(Enum):
    STUDENT = "STUDENT"
    ADMIN = "ADMIN"
    LECTURER = "LECTURER"
    BOT = "BOT"

class ChatStatus(str, Enum):
    OPEN = "OPEN"
    PENDING_AGENT = "PENDING_AGENT"
    AGENT_PROCESSING = "AGENT_PROCESSING"
    CLOSED = "CLOSED"

class MessageType(str, Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    FILE = "FILE"
    SYSTEM_EVENT = "SYSTEM_EVENT"

class AcademicStatus(str, Enum):
    ACTIVE = "ACTIVE"
    WARNING = "WARNING"
    DANGER = "DANGER"

class TrainingStatus(str, Enum):
    NEW = "NEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

from enum import Enum

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"

class AcademicStatus(str, Enum):
    ACTIVE = "active"
    WARNING = "warning"
    DANGER = "danger"