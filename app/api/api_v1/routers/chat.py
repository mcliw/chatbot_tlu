from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.api_v1 import deps
from app.services.chat_service import ChatService
from app.services.file_service import FileService
from app.schemas.chat_schema import ConversationResponse, PaginatedMessagesResponse
from app.shared.enums import ChatStatus, MessageType
from app.models.user import User

router = APIRouter()

@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(
    status: Optional[ChatStatus] = None,
    limit: int = 20,
    db: Session = Depends(deps.get_db),
    # Đổi tên thành _current_user để tránh cảnh báo unused variable
    _current_user: User = Depends(deps.get_current_active_superuser) 
):
    """
    Web Admin: Lấy danh sách hội thoại.
    """
    service = ChatService(db)
    return service.get_conversations(status, limit)

@router.get("/conversations/{conversation_id}/messages", response_model=PaginatedMessagesResponse)
def get_messages(
    conversation_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(deps.get_db),
    _current_user: User = Depends(deps.get_current_active_user)
):
    """
    Lấy lịch sử tin nhắn chi tiết.
    """
    service = ChatService(db)
    result = service.get_messages(conversation_id, page, size)
    
    return PaginatedMessagesResponse(
        total=result["total"],
        page=page,
        size=size,
        items=result["items"]
    )

@router.post("/conversations/{conversation_id}/assign")
async def assign_agent(
    conversation_id: str,
    agent_id: str = Query(..., description="ID của Admin/Agent được gán"),
    db: Session = Depends(deps.get_db),
    _current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Web Admin: Gán Agent.
    """
    service = ChatService(db)
    return await service.assign_agent(conversation_id, agent_id)

@router.put("/conversations/{conversation_id}/status")
async def update_status(
    conversation_id: str,
    status: ChatStatus,
    db: Session = Depends(deps.get_db),
    _current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Web Admin: Cập nhật trạng thái hội thoại.
    """
    service = ChatService(db)
    return await service.update_status(conversation_id, status)

@router.post("/upload", response_model=dict)
async def upload_chat_file(
    file: UploadFile = File(...),
    type: MessageType = Form(MessageType.IMAGE),
    _current_user: User = Depends(deps.get_current_active_user)
):
    """
    Upload ảnh/file khi chat.
    """
    file_service = FileService()
    
    if type == MessageType.IMAGE:
        sub_folder = "chat/images"
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/gif"]
    else:
        sub_folder = "chat/files"
        allowed_types = [
            "application/pdf", 
            "application/msword", 
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
            "application/vnd.ms-excel"
        ]

    try:
        file_url = await file_service.save_file(
            file=file, 
            sub_folder=sub_folder, 
            allowed_types=allowed_types
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Upload failed")
    
    return {
        "url": file_url,
        "type": type.value,
        "filename": file.filename
    }