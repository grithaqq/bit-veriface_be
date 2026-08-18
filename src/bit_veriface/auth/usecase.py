from uuid import UUID

from auth import domain
from core.security import get_password_hash
from shared import exceptions


class AuthUsecase:
    def __init__(self, repo: domain.AuthRepositoryBase, svc: domain.AuthServiceBase):
        self.repo = repo
        self.svc = svc

    def authenticate(self, email: str, password: str) -> domain.Token:
        user = self.repo.authenticate(email=email, password=password)
        if not user:
            raise exceptions.RepositoryException("Incorrect email or password")
        elif not user.is_active:
            raise exceptions.RepositoryException("Inactive user")

        token = self.svc.create_access_token(user.id)

        return token

    def recover_password(self, email: str) -> None:
        auth = self.repo.get_by_email(email=email)
        if not auth:
            raise exceptions.RepositoryException(
                "The user with this username does not exist in the system."
            )
        self.svc.recover_password(auth)

    def reset_password(self, token: str, password: str):
        auth_id = self.svc.verify_password_reset_token(token)
        if not auth_id:
            raise exceptions.ServiceException("Invalid token")

        auth = self.repo.get(id=UUID(auth_id))
        if not auth:
            raise exceptions.RepositoryException(
                "The user with this token does not exist in the system."
            )
        elif not self.repo.is_active(auth):
            raise exceptions.RepositoryException("Inactive user")

        hashed_password = get_password_hash(password)
        auth.hashed_password = hashed_password
        self.repo.update(id=UUID(auth_id), obj_in=auth)

    def test_token(self, current_user):
        return current_user
