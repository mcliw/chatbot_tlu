import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "TLU Chatbot"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:DEADlift12Hard@localhost:5432/chatbot_tlu")

settings = Settings()