from typing import Iterable
from sqlalchemy import select

from models.domain.jobs import Job
from bases.repositories.base_alchemy_repository import BaseAlchemyAsyncRepository
from models.dto import job_dto


def _job_to_dto(job: Job) -> job_dto.JobResponse:
    result = job_dto.JobResponse(
        id=job.id,
        user_id=job.user_id,
        title=job.title,
        description=job.description,
        salary_from=job.salary_from,
        salary_to=job.salary_to,
        is_active=job.is_active,
        created_at=job.created_at
    )
    return result


def _scalars_to_dto_list(scalars: Iterable[Job]) -> Iterable[job_dto.JobResponse]:
    jobs = []
    for job in scalars:
        jobs.append(_job_to_dto(job))
    return jobs


class JobRepository(BaseAlchemyAsyncRepository[Job]):
    async def create(self, job_data: job_dto.JobCreate, user_id) -> job_dto.JobResponse:
        """
            Создать нового пользователя
            :param job_data: DTO с данными для создания новой вакансии
            :param user_id: id текущего пользователя
        """
        session = await self.connection_proxy.connect()
        job_db = Job(
            user_id=user_id,
            title=job_data.title,
            description=job_data.description,
            salary_from=job_data.salary_from,
            salary_to=job_data.salary_to,
        )

        session.add(job_db)
        await session.flush()

        return _job_to_dto(job_db)

    async def retrieve(self, job_id: int) -> job_dto.JobResponse | None:
        """Получить вакансию по ID"""
        session = await self.connection_proxy.connect()
        job = await session.get(entity=Job, ident=job_id)
        if job:
            return _job_to_dto(job)
        else:
            return None

    async def list(self) -> Iterable[job_dto.JobResponse]:
        """Получить список всех вакансий (включая неактивные)"""
        stmt = select(Job)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        jobs = _scalars_to_dto_list(result.scalars().all())
        return jobs

    async def update(self, job_id: int, job_update: job_dto.JobUpdate) -> job_dto.JobResponse | None:
        """Обновить данные вакансии"""
        session = await self.connection_proxy.connect()

        job_db = await session.get(Job, job_id)
        if not job_db:
            return None

        update_data = job_update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(job_db, key, value)

        await session.flush()
        return _job_to_dto(job_db)

    async def delete(self, job_id: int) -> None:
        """Удалить вакансию"""
        session = await self.connection_proxy.connect()
        job = await session.get(Job, job_id)
        if job:
            await session.delete(job)

    async def get_active_jobs(self) -> Iterable[job_dto.JobResponse]:
        """Получить список всех вакансий (только активные)"""
        stmt = select(Job).where(Job.is_active is True)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        scalars = result.scalars().all()
        return _scalars_to_dto_list(scalars)

    async def get_jobs_by_user_id(self, user_id: int) -> Iterable[job_dto.JobResponse]:
        """Получить все вакансии, созданные конкретным работодателем (включая неактивные)."""
        stmt = select(Job).where(Job.user_id == user_id)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        scalars = result.scalars().all()
        return _scalars_to_dto_list(scalars)

    async def get_active_jobs_by_user_id(self, user_id: int) -> Iterable[job_dto.JobResponse]:
        """Получить все вакансии, созданные конкретным работодателем (только активные)."""
        stmt = select(Job).where(Job.user_id == user_id, Job.is_active is True)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        scalars = result.scalars().all()
        return _scalars_to_dto_list(scalars)
