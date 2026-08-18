from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from shared.schemas import BaseListResponse, BaseResponse


# Shared properties
class UploadedFileBase(BaseModel):
    original_filename: str
    saved_filename: str
    content_type: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    user_id: UUID


class UploadedFileCreate(BaseModel):
    pass


class UploadedFileGetResponse(BaseResponse):
    data: UploadedFileBase


class UploadedFileDelete(BaseResponse):
    pass


class UploadedFileUpdate(BaseModel):
    pass


class UploadedFileInDBBase(UploadedFileBase):
    id: Optional[UUID] = None
    model_config = ConfigDict(from_attributes=True)


class UploadedFileListResponse(BaseListResponse):
    data: List[UploadedFileInDBBase]


# Additional properties to return via API
class UploadedFile(UploadedFileInDBBase):
    pass


# Additional properties stored in DB
class UploadedFileInDB(UploadedFileInDBBase):
    hashed_password: str


class UploadedFileInMilvus(BaseModel):
    img_path: str
    img_id: UUID
    user_id: UUID


class SearchFileResponse(BaseModel):
    img_path: str
    img_id: UUID
    user_id: UUID
    distance: float


class ListUploadedFileInMilvus(BaseListResponse):
    data: List[SearchFileResponse]