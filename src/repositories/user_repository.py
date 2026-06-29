from typing import Iterable
from sqlalchemy import select, insert

from models.domain.users import User
from bases.repositories.base_alchemy_repository import BaseAlchemyAsyncRepository


class UserRepository(BaseAlchemyAsyncRepository[User]):

    async def create(self, data: dict) -> User:
        """Создать нового пользователя"""
        stmt = insert(User).values(**data).returning(User)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        return result.scalar_one()

    async def retrieve(self, user_id: int) -> User | None:
        """Получить пользователя по ID"""
        stmt = select(User).where(User.id == user_id)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self) -> Iterable[User]:
        """Получить список всех пользователей"""
        stmt = select(User)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_email(self, email: str) -> User | None:
        """Поиск по email"""
        stmt = select(User).where(User.email == email)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, *args, **kwargs) -> User:
        raise NotImplementedError()

    async def delete(self, *args, **kwargs):
        raise NotImplementedError()