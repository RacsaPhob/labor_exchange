from typing import Iterable
from sqlalchemy import select, insert, update, delete

from models.domain.responses import Response
from bases.repositories.base_alchemy_repository import BaseAlchemyAsyncRepository


class ResponseRepository(BaseAlchemyAsyncRepository[Response]):
    async def create(self, data: dict) -> Response:
        """Создать новый отклик на вакансию"""
        stmt = insert(Response).values(**data).returning(Response)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        return result.scalar_one()

    async def retrieve(self, response_id: int) -> Response | None:
        """Получить отклик по ID"""
        stmt = select(Response).where(Response.id == response_id)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self) -> Iterable[Response]:
        """Получить все отклики"""
        stmt = select(Response)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        return result.scalars().all()

    async def update(self, response_id: int, data: dict) -> Response | None:
        """Обновить отклик"""
        stmt = update(Response).where(Response.id == response_id).values(**data).returning(Response)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, response_id: int) -> None:
        """Удалить отклик"""
        stmt = delete(Response).where(Response.id == response_id)
        session = await self.connection_proxy.connect()
        await session.execute(stmt)

    async def get_by_job_id(self, job_id: int) -> Iterable[Response]:
        """Получить все отклики на конкретную вакансию."""
        stmt = select(Response).where(Response.job_id == job_id)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_user_id(self, user_id: int) -> Iterable[Response]:
        """Получить все отклики конкретного пользователя."""
        stmt = select(Response).where(Response.user_id == user_id)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        return result.scalars().all()

    async def check_exists(self, user_id: int, job_id: int) -> bool:
        """Проверить, откликался ли уже этот пользователь на эту вакансию."""
        stmt = select(Response).where(Response.user_id == user_id, Response.job_id == job_id)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        return result.first() is not None
