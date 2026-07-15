from typing import Iterable

from bases.services.base_service import BaseService
from bases.uows.response_uow import ResponseUOW
from models.dto import response_dto

from services.user_service import UserService
from services.exceptions import (ObjectExistsException, ObjectDoesntExistsException,
                                 NoPermissionException)


class ResponseService(BaseService):

    def __init__(self, uow: ResponseUOW, user_service: UserService) -> None:
        self.uow = uow
        self.user_service = user_service

    async def create_response(self, user_id: int,
                              response_in: response_dto.ResponseCreate) -> response_dto.Response:
        """Создание нового отклика"""

        user = await self.user_service.get_user_by_id(user_id)
        async with self.uow as uow:

            if not user.is_company:
                already_exists = await uow.repository.check_exists(user_id, response_in.job_id)
                if already_exists:
                    raise ObjectExistsException("Вы уже откликались на эту вакансию")

                response = await uow.repository.create(response_in, user_id)
                await uow.commit()

                return response
            raise NoPermissionException("Откликаться на вакансии может только соискатель")

    async def get_response_by_id(self, response_id: int) -> response_dto.Response:
        """Получить отклик по id"""
        async with self.uow as uow:
            response = await uow.repository.retrieve(response_id)
            if not response:
                raise ObjectDoesntExistsException("Отклик не найден")

            return response

    async def get_response_by_user_id_and_job_id(self, user_id: int, job_id: int) -> response_dto.Response:
        """Получить отклик по id пользователя и вакансии"""
        async with self.uow as uow:
            response = await uow.repository.retrieve_by_user_id_and_job_id(user_id, job_id)
            if not response:
                raise ObjectDoesntExistsException("Отклик не найдена")

            return response

    async def get_user_responses(self, user_id: int) -> Iterable[response_dto.Response]:
        """Получить все отклики соискателя"""
        async with self.uow as uow:
            return await uow.repository.get_by_user_id(user_id)

    async def get_job_responses(self, job_id: int) -> Iterable[response_dto.Response]:
        """
        Получить все отклики на конкретную вакансию.
        """
        async with self.uow as uow:
            return await uow.repository.get_by_job_id(job_id)

    async def get_all_responses(self) -> Iterable[response_dto.Response]:
        """Получить все отклики."""
        async with self.uow as uow:
            return await uow.repository.list()

    async def update_response(self, response_id: int, current_user_id: int,
                              response_in: response_dto.ResponseUpdate) -> response_dto.Response:
        """Обновление вакансии с проверкой прав доступа"""
        async with self.uow as uow:

            response = await uow.repository.retrieve(response_id)
            if not response:
                raise ObjectDoesntExistsException("Отклик не найден")

            if response.user_id != current_user_id:
                raise NoPermissionException("Вы не можете редактировать чужой отклик")

            updated_response = await uow.repository.update(response_id, response_in)
            await uow.commit()

            return updated_response

    async def delete_response(self, response_id: int, current_user_id: int) -> None:
        """Удаление отклика"""
        async with self.uow as uow:

            response = await uow.repository.retrieve(response_id)
            if not response:
                raise ObjectDoesntExistsException("Отклик не найден")

            if response.user_id != current_user_id:
                raise NoPermissionException("Вы не можете удалить чужой отклик")

            await uow.repository.delete(response_id)
            await uow.commit()
