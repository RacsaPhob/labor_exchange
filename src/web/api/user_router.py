from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from typing import Iterable

from models.dto import user_dto
from services.user_service import UserService

from tools.di_containers.service_container import Container
from tools.security.jwt_tools import create_access_token

from models.dto.jwt_token_dto import TokenResponse
router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=user_dto.UserResponse)
@inject
async def register(
    user_in: user_dto.UserCreate,
    service: UserService = Depends(Provide[Container.user_service])
):
    try:
        result = await service.register_user(user_in)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует",
        )
    return result


@router.get("/get_by_id", response_model=user_dto.UserResponse)
@inject
async def get_by_id(
    user_id: int,
    service: UserService = Depends(Provide[Container.user_service])
):
    try:
        return await service.get_user_by_id(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким id не найден"
        )


@router.get("/get_by_email", response_model=user_dto.UserResponse)
@inject
async def get_by_email(
    user_email: str,
    service: UserService = Depends(Provide[Container.user_service])
):
    try:
        return await service.get_user_by_email(user_email)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким email не найден"
        )


@router.post("/login", response_model=TokenResponse)
@inject
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        user_service: UserService = Depends(Provide[Container.user_service])
):
    """Вход в систему (получение JWT токена)."""

    user = await user_service.authenticate_user(
        email=form_data.username,
        password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(access_token=access_token, token_type="bearer")


@router.get("/get_all_users", response_model=Iterable[user_dto.UserResponse])
@inject
async def get_all_users(
    service: UserService = Depends(Provide[Container.user_service])
):
    return await service.get_all_users()
