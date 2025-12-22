# app/services/file_service.py
import os
import shutil
import uuid
from fastapi import UploadFile, HTTPException
from typing import List
import logging

logger = logging.getLogger(__name__)

UPLOAD_DIR = "static/uploads/avatars"

class FileService:
    def __init__(self):
        # Tạo thư mục nếu chưa tồn tại
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

    async def save_avatar(self, file: UploadFile, old_avatar_path: str = None) -> str:
        """
        Lưu file avatar, xóa file cũ nếu có.
        Rollback (xóa file mới) nếu lỗi xảy ra.
        """
        if not file:
            return None
        
        # Validation file type
        if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
            raise HTTPException(status_code=400, detail="Only JPEG/PNG images are allowed.")

        # Validate file size (ví dụ < 2MB) - Check bằng content-length header hoặc đọc chunk
        
        # Tạo tên file unique
        file_extension = file.filename.split(".")[-1]
        new_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, new_filename)

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"File uploaded successfully: {file_path}")

            # Xóa file cũ nếu tồn tại (Clean up)
            if old_avatar_path and os.path.exists(old_avatar_path):
                try:
                    os.remove(old_avatar_path)
                    logger.info(f"Old avatar removed: {old_avatar_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove old avatar: {e}")

            # Trả về đường dẫn tương đối để lưu DB
            return file_path

        except Exception as e:
            # Rollback: Xóa file mới tạo nếu quá trình lưu lỗi
            if os.path.exists(file_path):
                os.remove(file_path)
            logger.error(f"Error saving file: {e}")
            raise HTTPException(status_code=500, detail="Could not save file")