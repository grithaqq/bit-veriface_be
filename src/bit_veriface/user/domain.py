from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from shared import entity


@dataclass
class User:
    id: Optional[UUID] = field(default=None)
    full_name: Optional[str] = field(default=None)
    email: Optional[str] = field(default=None)
    hashed_password: Optional[str] = field(default=None)
    password: Optional[str] = field(default=None)
    is_active: bool = field(default=True)
    is_superuser: bool = field(default=False)
    created_at: Optional[datetime] = field(default=None)
    updated_at: Optional[datetime] = field(default=None)


@dataclass
class BaseUserResponse(entity.BaseResponse):
    data: User = field(default=None)


@dataclass
class BaseListUserResponse(entity.BaseListResponse):
    data: List[User] = field(default=None)


class UserRepositoryBase(ABC):
    @abstractmethod
    def count(self) -> int:
        pass

    # @abstractmethod
    # def count_by_user_id(self, user_id: UUID):
    #     pass

    @abstractmethod
    def get_by_email(self, *, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[User]:
        pass

    @abstractmethod
    def get(self, *, id: UUID) -> User:
        pass

    @abstractmethod
    def create(self, *, obj_in: User) -> User:
        pass

    @abstractmethod
    def update(self, *, db_obj: User, obj_in: User) -> User:
        pass

    @abstractmethod
    def remove(self, *, id: UUID) -> User:
        pass

    @abstractmethod
    def authenticate(self, *, email: str, password: str) -> Optional[User]:
        pass

    @abstractmethod
    def is_active(self, user: User) -> bool:
        pass

    @abstractmethod
    def is_superuser(self, user: User) -> bool:
        pass


class UserServiceBase(ABC):
    # @abstractmethod
    # def send_email(
    #     self,
    #     email_to: str,
    #     subject_template: str = "",
    #     html_template: str = "",
    #     environment: Dict[str, Any] = {},
    # ) -> None:
    #     pass

    @abstractmethod
    def send_new_account_email(self, email_to, username, password) -> None:
        pass

    @abstractmethod
    def send_reset_password_email(email_to: str, email: str, token: str) -> None:
        pass

    @abstractmethod
    def send_test_email(self, email_to: str) -> None:
        pass
