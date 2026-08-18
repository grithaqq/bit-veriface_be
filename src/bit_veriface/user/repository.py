import dataclasses
from typing import List, Optional
from uuid import UUID

from core.security import get_password_hash, verify_password
from dbase import models
from sqlalchemy.orm import Session
from user import domain


class UserV2Repository(domain.UserRepositoryBase):
    def __init__(self, session: Session):
        self.session = session

    def count(self):
        return self.session.query(models.User).count()

    def get_by_email(self, email: str) -> domain.User:
        return (
            self.session.query(models.User).filter(models.User.email == email).first()
        )

    def get_multi(self, skip: int = 0, limit: int = 100) -> List[domain.User]:
        users = self.session.query(models.User).offset(skip).limit(limit).all()
        list_user = [u.to_entity() for u in users]
        return list_user

    def get(self, id: UUID) -> domain.User:
        user = self.session.query(models.User).filter(models.User.id == id).first()
        return user.to_entity()

    def create(self, *, obj_in: domain.User) -> domain.User:
        db_obj = models.User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
        )
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def update(self, *, id: UUID, obj_in: domain.User) -> domain.User:
        db_obj = self.get(id=id)
        # if db_obj is empty than raise exception
        if not db_obj:
            raise Exception("User not found")

        for field in dataclasses.fields(obj_in):
            value = getattr(obj_in, field.name)
            if value is not None:  # Assuming you want to ignore None values
                if field.name == "password":
                    # Assuming `get_password_hash` is a function you've defined elsewhere
                    db_obj.hashed_password = get_password_hash(value)
                    setattr(db_obj, field.name, value)
                else:
                    setattr(db_obj, field.name, value)

        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)

        return db_obj

    def remove(self, *, id: UUID) -> domain.User:
        obj = self.get(id=id)
        self.session.delete(obj)
        self.session.commit()
        return obj

    def authenticate(self, email: str, password: str) -> Optional[domain.User]:
        user = self.get_by_email(email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: domain.User) -> bool:
        return user.is_active

    def is_superuser(self, user: domain.User) -> bool:
        return user.is_superuser
