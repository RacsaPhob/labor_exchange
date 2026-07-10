from typing import Iterable

from bases.services.base_service import BaseService
from bases.uows.job_uow import JobUOW
from models.dto import job_dto

from services.user_service import UserService


class JobService(BaseService):
    def __init__(self, uow: JobUOW, user_service: UserService) -> None:
        self.uow = uow
        self.user_service = user_service

    async def create_job(self, current_user_id: int, job_in: job_dto.JobCreate) -> job_dto.JobResponse:
        user = await  self.user_service.get_user_by_id(current_user_id)
        """Создание новой вакансии"""
        async with self.uow as uow:

            if user.is_company:
                # привязываем вакансию к тому, кто делает запрос
                new_job_dto = await uow.repository.create(job_in, current_user_id)
                await uow.commit()
                return new_job_dto

            raise PermissionError("Соискатель не может создать вакансию")

    async def get_active_jobs(self) -> Iterable[job_dto.JobResponse]:
        """Получить список всех активных вакансий"""
        async with self.uow as uow:

            return await uow.repository.get_active_jobs()

    async def get_job_by_id(self, job_id: int) -> job_dto.JobResponse:
        """Получить вакансию по id"""
        async with self.uow as uow:
            job = await uow.repository.retrieve(job_id)
            if not job:
                raise ValueError("Вакансия не найдена")

            return job

    async def update_job(self, job_id: int, current_user_id: int, job_in: job_dto.JobUpdate) -> job_dto.JobResponse:
        """Обновление вакансии с проверкой прав доступа"""
        async with self.uow as uow:

            job = await uow.repository.retrieve(job_id)
            if not job:
                raise ValueError("Вакансия не найдена")

            if job.user_id != current_user_id:
                raise PermissionError("Вы не можете редактировать чужую вакансию")

            updated_job = await uow.repository.update(job_id, job_in)
            await uow.commit()

            return updated_job

    async def delete_job(self, job_id: int, current_user_id: int) -> None:
        """Удаление вакансии"""
        async with self.uow as uow:
            job = await uow.repository.retrieve(job_id)
            if not job:
                raise ValueError("Вакансия не найдена")

            if job.user_id != current_user_id:
                raise PermissionError("Вы не можете удалить чужую вакансию")

            await uow.repository.delete(job_id)
            await uow.commit()

    async def get_active_user_jobs(self, user_id):
        """Получить все активные вакансии работодателя"""
        async with self.uow as uow:
            jobs = await uow.repository.get_active_jobs_by_user_id(user_id)
            return jobs

    async def get_all_user_jobs(self, user_id):
        """Получить все вакансии работодателя"""
        async with self.uow as uow:
            jobs = await uow.repository.get_jobs_by_user_id(user_id)
            return jobs

    async def get_all_jobs(self):
        """Получить все вакансии"""
        async with self.uow as uow:
            jobs = await uow.repository.list()
            return jobs

