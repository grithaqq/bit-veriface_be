from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Auth:
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
class Token:
    access_token: str
    token_type: str


class AuthRepositoryBase(ABC):
    @abstractmethod
    def get_by_email(self, *, email: str) -> Optional[Auth]:
        pass

    @abstractmethod
    def get(self, *, id: UUID) -> Optional[Auth]:
        pass

    @abstractmethod
    def authenticate(self, *, email: str, password: str) -> Optional[Auth]:
        pass

    @abstractmethod
    def update(self, id: UUID, auth: Auth):
        pass

    @abstractmethod
    def is_active(self, user: Auth) -> bool:
        pass

    @abstractmethod
    def is_superuser(self, user: Auth) -> bool:
        pass


class AuthServiceBase(ABC):
    @abstractmethod
    def create_access_token(self, data: dict) -> Token:
        pass

    @abstractmethod
    def recover_password(self, auth: Auth):
        pass

    @abstractmethod
    def verify_password_reset_token(self, token: str) -> str:
        pass

    @abstractmethod
    def generate_password_reset_token(self, email: str) -> str:
        pass
