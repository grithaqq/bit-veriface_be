from uuid import UUID

from shared import exceptions, paginator
from user import domain


class UserUsecase:
    def __init__(self, repo: domain.UserRepositoryBase, svc: domain.UserServiceBase):
        self.repo = repo
        self.svc = svc

    def get(self, id: UUID, current_user: domain.User) -> domain.User:
        user = self.repo.get(id=id)
        if user == current_user:
            return user
        if not user:
            raise exceptions.RepositoryException("User not found")
        if not current_user.is_superuser:
            raise exceptions.RepositoryException(
                "The user doesn't have enough privileges"
            )

        return user

    def create(self, user_obj: domain.User, send_email=False) -> domain.User:
        user = self.repo.get_by_email(email=user_obj.email)
        if user:
            raise exceptions.RepositoryException("User already exists")
        user = self.repo.create(obj_in=user_obj)
        if send_email:
            try:
                self.svc.send_new_account_email(
                    email_to=user_obj.email,
                    username=user_obj.email,
                    password=user_obj.password,
                )
            except exceptions.ServiceException as e:
                raise exceptions.ServiceException("Failed to send email")
        return user

    def get_multi(
        self, current_user, skip: int = 0, limit: int = 100
    ) -> domain.BaseListUserResponse:
        if not current_user.is_superuser:
            raise exceptions.RepositoryException(
                "The user doesn't have enough privileges"
            )
        total = self.repo.count()
        users = self.repo.get_multi(skip=skip, limit=limit)
        pagination = paginator.paginate_data(total=total, skip=skip, limit=limit)

        return domain.BaseListUserResponse(
            status=200,
            data=users,
            pagination=pagination,
            message="Get users successfully",
        )

    def update(self, id: UUID, user_in: domain.User) -> domain.User:
        user = self.repo.get(id=id)
        if not user:
            raise exceptions.RepositoryException(
                f"The user with this user_id={str(id)} not exist in the system"
            )
        user = self.repo.update(id=id, obj_in=user_in)
        return user
