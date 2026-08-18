from dataclasses import asdict
from typing import Any
from uuid import UUID

from core import deps
from core.config import settings
from dbase import models
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from shared import exceptions
from sqlalchemy.orm import Session
from user import repository, schemas, service, usecase

router = APIRouter()


def user_usecase(session: Session = Depends(deps.get_db)):
    repo = repository.UserV2Repository(session)
    svc = service.UserService()
    ucase = usecase.UserUsecase(repo, svc)
    return ucase


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
    ucase: usecase.UserUsecase = Depends(user_usecase),
) -> Any:
    """
    Get a specific user by id.
    """
    try:
        user = ucase.get(id=UUID(user_id), current_user=current_user)
    except exceptions.RepositoryException as e:
        raise HTTPException(status_code=400, detail=e.message)
    except exceptions.ServiceException as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)
    return user


@router.get("/")
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    ucase: usecase.UserUsecase = Depends(user_usecase),
) -> Any:
    """
    Retrieve users.
    """
    try:
        user_list = ucase.get_multi(current_user=current_user, skip=skip, limit=limit)

    except exceptions.RepositoryException as e:
        raise HTTPException(status_code=400, detail=e.message)
    except exceptions.ServiceException as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)
    response = schemas.ListUserResponse(
        **asdict(user_list),
    )
    return response


@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    ucase: usecase.UserUsecase = Depends(user_usecase),
) -> Any:
    """
    Create new user.
    """
    user_entity = user_in.to_entity()
    try:
        user = ucase.create(user_obj=user_entity, send_email=settings.EMAILS_ENABLED)
    except exceptions.RepositoryException as e:
        raise HTTPException(status_code=400, detail=e.message)
    except exceptions.ServiceException as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

    return user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: str,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    ucase: usecase.UserUsecase = Depends(user_usecase),
) -> Any:
    """
    Update a user.
    """
    user_entity = user_in.to_entity()
    try:
        user = ucase.update(id=UUID(user_id), user_in=user_entity)
    except exceptions.RepositoryException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except exceptions.ServiceException as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

    return user


@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
    ucase: usecase.UserUsecase = Depends(user_usecase),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email

    user_entity = user_in.to_entity()

    try:
        user = ucase.update(id=current_user.id, user_in=user_entity)
    except exceptions.RepositoryException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except exceptions.ServiceException as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

    return user
