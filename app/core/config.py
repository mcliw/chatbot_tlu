import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY", "mac-dinh-neu-thieu-env-thi-dung-cai-nay-de-khong-loi")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TLU Chatbot"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:DEADlift12Hard@localhost:5432/chatbot_tlu")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()