import os
import shutil
import uuid
import logging
from typing import List, Optional
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

# Thư mục gốc để lưu trữ
BASE_UPLOAD_DIR = "static/uploads"

class FileService:
    def __init__(self):
        # Tạo thư mục gốc nếu chưa tồn tại
        if not os.path.exists(BASE_UPLOAD_DIR):
            os.makedirs(BASE_UPLOAD_DIR)

    async def save_file(self, file: UploadFile, sub_folder: str, allowed_types: Optional[List[str]] = None) -> str:
        """
        Hàm dùng chung để lưu file.
        Trả về đường dẫn tương đối (relative path) chuẩn URL (dùng dấu /).
        """
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")

        # 1. Validate loại file (nếu có yêu cầu)
        if allowed_types:
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
                )

        # 2. Tạo đường dẫn thư mục đích
        target_folder = os.path.join(BASE_UPLOAD_DIR, sub_folder)
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        # 3. Tạo tên file unique (UUID)
        file_ext = os.path.splitext(file.filename)[1]
        if not file_ext:
             file_ext = "" # Fallback nếu không có đuôi file
        
        new_filename = f"{uuid.uuid4()}{file_ext}"
        
        # Đường dẫn hệ thống để lưu file (OS specific path separator)
        file_sys_path = os.path.join(target_folder, new_filename)

        # 4. Lưu file vào ổ cứng
        try:
            with open(file_sys_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"File uploaded successfully to: {file_sys_path}")
            
            # 5. Trả về đường dẫn chuẩn URL (Forward slash) để lưu DB
            # Ví dụ: static/uploads/avatars/abc.jpg
            relative_path = os.path.join(BASE_UPLOAD_DIR, sub_folder, new_filename)
            return relative_path.replace("\\", "/")

        except Exception as e:
            # Rollback: Xóa file nếu lỗi trong quá trình ghi
            if os.path.exists(file_sys_path):
                os.remove(file_sys_path)
            logger.error(f"Error saving file: {e}")
            raise HTTPException(status_code=500, detail="Could not save file")

    async def save_avatar(self, file: UploadFile, old_avatar_path: str = None) -> str:
        """
        Wrapper cho save_file chuyên dùng cho Avatar.
        Có xử lý xóa avatar cũ.
        """
        AVATAR_ALLOWED_TYPES = ["image/jpeg", "image/png", "image/jpg"]
        
        # Gọi hàm save_file chung
        new_file_path = await self.save_file(
            file=file, 
            sub_folder="avatars", 
            allowed_types=AVATAR_ALLOWED_TYPES
        )

        # Xóa file cũ nếu tồn tại (Clean up)
        if old_avatar_path:
            try:
                # Xử lý đường dẫn cũ: Bỏ dấu '/' ở đầu nếu có để os.path.exists hiểu đúng
                # Ví dụ DB lưu: /static/uploads/... -> cần convert thành static/uploads/...
                clean_old_path = old_avatar_path.lstrip("/")
                clean_old_path = clean_old_path.replace("/", os.sep) # Convert về separator của OS

                if os.path.exists(clean_old_path):
                    os.remove(clean_old_path)
                    logger.info(f"Old avatar removed: {clean_old_path}")
            except Exception as e:
                # Chỉ log warning, không raise lỗi để tránh failed request update
                logger.warning(f"Failed to remove old avatar: {e}")

        return new_file_path