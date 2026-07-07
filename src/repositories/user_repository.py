from typing import Iterable
from sqlalchemy import select

from models.domain.users import User
from bases.repositories.base_alchemy_repository import BaseAlchemyAsyncRepository
from models.dto import user_dto


def _user_to_dto(user: User) -> user_dto.UserResponse:
    result = user_dto.UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        is_company=user.is_company,
        created_at=user.created_at,
    )
    return result


def _scalars_to_dto_list(scalars: Iterable[User]) -> Iterable[user_dto.UserResponse]:
    users = []
    for user in scalars:
        users.append(_user_to_dto(user))
    return users


class UserRepository(BaseAlchemyAsyncRepository[User]):
    async def create(self, user_data: user_dto.UserCreate) -> user_dto.UserResponse:
        """
            Создать нового пользователя
            :param user_data: DTO с данными для создания нового пользователя
        """
        session = await self.connection_proxy.connect()
        user_db = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=user_data.password,
            is_company=user_data.is_company
        )

        session.add(user_db)
        await session.flush()

        return _user_to_dto(user_db)

    async def retrieve(self, user_id: int) -> user_dto.UserResponse | None:
        """Получить пользователя по ID"""
        session = await self.connection_proxy.connect()
        user = await session.get(entity=User, ident=user_id)
        if user:
            return _user_to_dto(user)
        else:
            return None

    async def list(self) -> Iterable[user_dto.UserResponse]:
        """Получить список всех пользователей"""
        stmt = select(User)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        users = _scalars_to_dto_list(result.scalars().all())
        return users

    async def get_by_email(self, email: str) -> user_dto.UserResponse| None:
        """Поиск по email"""
        stmt = select(User).where(User.email == email)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            result = user_dto.UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                is_company=user.is_company,
                created_at=user.created_at,
            )
            return result
        return None

    async def get_by_email_with_password(self, email: str) -> user_dto.UserResponseWithPassword| None:
        """Поиск по email. В DTO есть поле с хешем пароля"""
        stmt = select(User).where(User.email == email)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            result = user_dto.UserResponseWithPassword(
                id=user.id,
                email=user.email,
                username=user.username,
                is_company=user.is_company,
                created_at=user.created_at,
                hashed_password=user.hashed_password
            )
            return result
        return None

    async def update(self, *args, **kwargs) -> User:
        raise NotImplementedError()

    async def delete(self, *args, **kwargs) -> None:
        raise NotImplementedError()
