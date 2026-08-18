import dataclasses
from typing import Optional
from uuid import UUID

from auth import domain
from core.security import get_password_hash, verify_password
from dbase import models
from sqlalchemy.orm import Session


class AuthRepository(domain.AuthRepositoryBase):
    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> domain.Auth:
        return (
            self.session.query(models.User).filter(models.User.email == email).first()
        )

    def get(self, id: UUID) -> domain.Auth:
        user = user = (
            self.session.query(models.User).filter(models.User.id == id).first()
        )
        if user:
            return domain.Auth(
                id=user.id,
                email=user.email,
                hashed_password=user.hashed_password,
                full_name=user.full_name,
                is_superuser=user.is_superuser,
                is_active=user.is_active,
            )
        return None

    def update(self, *, id: UUID, obj_in: domain.Auth) -> domain.Auth:
        db_obj = self.session.query(models.User).filter(models.User.id == id).first()
        # if db_obj is empty than raise exception
        if not db_obj:
            raise Exception("User not found")

        for field in dataclasses.fields(obj_in):
            value = getattr(obj_in, field.name)
            if value is not None:  # Assuming you want to ignore None values
                if field.name == "password":
                    # Assuming `get_password_hash` is a function you've defined elsewhere
                    db_obj.hashed_password = get_password_hash(value)
                else:
                    setattr(db_obj, field.name, value)

        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)

        return db_obj

    def authenticate(self, *, email: str, password: str) -> Optional[domain.Auth]:
        auth = self.get_by_email(email=email)
        if not auth:
            return None
        if not verify_password(password, auth.hashed_password):
            return None
        return auth

    def is_active(self, auth: domain.Auth) -> bool:
        return auth.is_active

    def is_superuser(self, auth: domain.Auth) -> bool:
        return auth.is_superuser
