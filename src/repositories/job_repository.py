from typing import Iterable
from sqlalchemy import select, insert, update, delete

from models.domain.jobs import Job
from bases.repositories.base_alchemy_repository import BaseAlchemyAsyncRepository


class JobRepository(BaseAlchemyAsyncRepository[Job]):
    async def create(self, data: dict) -> Job:
        """Создать новую вакансию"""
        stmt = insert(Job).values(**data).returning(Job)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        return result.scalar_one()

    async def retrieve(self, job_id: int) -> Job | None:
        """Получить вакансию по ID"""
        stmt = select(Job).where(Job.id == job_id)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self) -> Iterable[Job]:
        """Получить список всех вакансий (включая неактивные)"""
        stmt = select(Job)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        return result.scalars().all()

    async def update(self, job_id: int, data: dict) -> Job | None:
        """Обновить данные вакансии"""
        stmt = update(Job).where(Job.id == job_id).values(**data).returning(Job)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, job_id: int) -> None:
        """Удалить вакансию"""
        stmt = delete(Job).where(Job.id == job_id)
        session = await self.connection_proxy.connect()
        await session.execute(stmt)

    async def get_active_jobs(self) -> Iterable[Job]:
        """Получить список всех вакансий (только активные)"""
        stmt = select(Job).where(Job.is_active is True)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_jobs_by_user_id(self, user_id: int) -> Iterable[Job]:
        """Получить все вакансии, созданные конкретным работодателем (включая неактивные)."""
        stmt = select(Job).where(Job.user_id == user_id)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_active_jobs_by_user_id(self, user_id: int) -> Iterable[Job]:
        """Получить все вакансии, созданные конкретным работодателем (только активные)."""
        stmt = select(Job).where(Job.user_id == user_id, Job.is_active is True)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        return result.scalars().all()
