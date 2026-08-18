from typing import Any

from auth import repository, schemas, service, usecase
from core import deps
from dbase import models
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from shared import exceptions
from shared import schemas as shared_schemas
from sqlalchemy.orm import Session
from user import schemas as user_schemas

router = APIRouter()


def auth_usecase(session: Session = Depends(deps.get_db)):
    repo = repository.AuthRepository(session)
    svc = service.AuthService()
    ucase = usecase.AuthUsecase(repo, svc)
    return ucase


@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    ucase: usecase.AuthUsecase = Depends(auth_usecase),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        token = ucase.authenticate(
            email=form_data.username, password=form_data.password
        )
    except exceptions.RepositoryException as e:
        raise HTTPException(status_code=400, detail=e.message)
    except exceptions.ServiceException as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)
    return token


@router.post("/login/test-token", response_model=user_schemas.User)
def test_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}", response_model=shared_schemas.Msg)
def recover_password(
    email: str,
    db: Session = Depends(deps.get_db),
    ucase: usecase.AuthUsecase = Depends(auth_usecase),
) -> Any:
    """
    Password Recovery
    """
    try:
        ucase.recover_password(email=email)
    except exceptions.RepositoryException as e:
        raise HTTPException(status_code=400, detail=e.message)
    except exceptions.ServiceException as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

    return {"msg": "Password recovery email sent"}


@router.post("/reset-password/", response_model=shared_schemas.Msg)
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(deps.get_db),
    ucase: usecase.AuthUsecase = Depends(auth_usecase),
) -> Any:
    """
    Reset password
    """
    try:
        ucase.reset_password(token=token, password=new_password)
    except exceptions.RepositoryException as e:
        raise HTTPException(status_code=400, detail=e.message)
    except exceptions.ServiceException as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

    return {"msg": "Password updated successfully"}
