from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from shared import entity
from user.domain import User


@dataclass
class UploadFile:
    id: Optional[UUID] = field(default=None)
    original_filename: str = field(default=None)
    saved_filename: str = field(default=None)
    content_type: str = field(default=None)
    created_at: Optional[datetime] = field(default=None)
    modified_at: Optional[datetime] = field(default=None)
    user_id: Optional[UUID] = field(default=None)
    user: Optional[User] = field(default=None)


@dataclass
class ListUploadedFile(entity.BaseListResponse):
    data: List[UploadFile] = field(default=None)


class FileIORepositoryBase(ABC):
    @abstractmethod
    def get_multi(self, subpath: str) -> List[UploadFile]:
        pass

    @abstractmethod
    def save(self, filename: str, data: bytes, subpath: str) -> None:
        pass

    @abstractmethod
    def replace(
        self, old_filename: str, new_filename: str, data: bytes, subpath: str
    ) -> None:
        pass

    @abstractmethod
    def remove(self, filename: str, subpath: str, image_id: str) -> None:
        pass

    @abstractmethod
    def count(self) -> int:
        pass


class UploadFileRepositoryBase(ABC):
    @abstractmethod
    def get(self, *, id: UUID) -> List[UploadFile]:
        pass

    @abstractmethod
    def get_multi_by_user_id(
        self, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[UploadFile]:
        pass

    @abstractmethod
    def create(self, *, obj_in: UploadFile) -> UploadFile:
        pass

    @abstractmethod
    def update(self, *, db_obj: UploadFile, obj_in: UploadFile) -> UploadFile:
        pass

    @abstractmethod
    def remove(self, *, id: UUID) -> UploadFile:
        pass

    @abstractmethod
    def count(self, user_id: UUID) -> int:
        pass

    @abstractmethod
    def search(self, skip: int, limit: int, upfile: UploadFile) -> List[UploadFile]:
        pass
