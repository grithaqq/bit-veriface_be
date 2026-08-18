import logging
from datetime import datetime, timedelta
from typing import *
from uuid import UUID

from auth import domain
from core import security
from core.config import settings
from jose import jwt
from utils import send_reset_password_email

log = logging.getLogger("uvicorn")


class AuthService(domain.AuthServiceBase):
    def __init__(self):
        pass

    def create_access_token(self, user_id: UUID) -> domain.Token:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            subject=user_id, expires_delta=access_token_expires
        )

        return domain.Token(access_token=access_token, token_type="bearer")

    def recover_password(self, auth: domain.Auth) -> None:
        password_reset_token = self.generate_password_reset_token(email=auth.email)
        send_reset_password_email(
            email_to=auth.email, email=auth.email, token=password_reset_token
        )

    def reset_password(self, auth: domain.Auth):
        pass

    def generate_password_reset_token(self, email: str) -> str:
        delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
        now = datetime.utcnow()
        expires = now + delta
        exp = expires.timestamp()
        encoded_jwt = jwt.encode(
            {"exp": exp, "nbf": now, "sub": email},
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        return encoded_jwt

    def verify_password_reset_token(self, token: str) -> Optional[str]:
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            return decoded_token["sub"]
        except jwt.JWTError as e:
            return None
