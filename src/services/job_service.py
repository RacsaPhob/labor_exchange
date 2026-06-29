from typing import List

from bases.services.base_service import BaseService
from bases.uows.job_uow import JobUOW
from models.dto import job_dto


class JobService(BaseService):
    def __init__(self, uow: JobUOW) -> None:
        self.uow = uow

    async def create_job(self, current_user_id: int, job_in: job_dto.JobCreate) -> job_dto.JobResponse:
        """Создание новой вакансии"""
        async with self.uow as uow:
            job_data = job_in.model_dump()

            # привязываем вакансию к тому, кто делает запрос
            job_data["user_id"] = current_user_id
            new_job_model = await uow.repository.create(job_data)
            await uow.commit()

            return job_dto.JobResponse.model_validate(new_job_model)

    async def get_active_jobs(self) -> List[job_dto.JobResponse]:
        """Получить список всех активных вакансий"""
        async with self.uow as uow:
            jobs_models = await uow.repository.get_active_jobs()

            return [job_dto.JobResponse.model_validate(job) for job in jobs_models]

    async def get_job_by_id(self, job_id: int) -> job_dto.JobResponse:
        """Получить вакансию по id"""
        async with self.uow as uow:
            job_model = await uow.repository.retrieve(job_id)
            if not job_model:
                raise ValueError("Вакансия не найдена")

            return job_dto.JobResponse.model_validate(job_model)

    async def update_job(self, job_id: int, current_user_id: int, job_in: job_dto.JobUpdate) -> job_dto.JobResponse:
        """Обновление вакансии с проверкой прав доступа"""
        async with self.uow as uow:

            job_model = await uow.repository.retrieve(job_id)
            if not job_model:
                raise ValueError("Вакансия не найдена")

            if job_model.user_id != current_user_id:
                raise PermissionError("Вы не можете редактировать чужую вакансию")

            update_data = job_in.model_dump(exclude_unset=True)
            updated_job_model = await uow.repository.update(job_id, update_data)
            await uow.commit()

            return job_dto.JobResponse.model_validate(updated_job_model)

    async def archive_job(self, job_id: int, current_user_id: int) -> None:
        """Перевод в неактивные"""
        async with self.uow as uow:

            job_model = await uow.repository.retrieve(job_id)
            if not job_model:
                raise ValueError("Вакансия не найдена")

            if job_model.user_id != current_user_id:
                raise PermissionError("Вы не можете удалить чужую вакансию")

            await uow.repository.update(job_id, {"is_active": False})
            await uow.commit()

    async def delete_job(self, job_id: int, current_user_id: int) -> None:
        """Удаление вакансии"""
        async with self.uow as uow:
            job_model = await uow.repository.retrieve(job_id)
            if not job_model:
                raise ValueError("Вакансия не найдена")

            if job_model.user_id != current_user_id:
                raise PermissionError("Вы не можете удалить чужую вакансию")

            await uow.repository.delete(job_id)
            await uow.commit()
