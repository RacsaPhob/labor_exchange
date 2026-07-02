from typing import Iterable

from bases.services.base_service import BaseService
from bases.uows.response_uow import ResponseUOW
from models.dto import response_dto


class ResponseService(BaseService):

    def __init__(self, uow: ResponseUOW) -> None:
        self.uow = uow

    async def create_response(self, user_id: int,
                              response_in: response_dto.ResponseCreate) -> response_dto.Response:
        """Создание нового отклика"""

        async with self.uow as uow:
            already_exists = await uow.repository.check_exists(user_id, response_in.job_id)
            if already_exists:
                raise ValueError("Вы уже откликались на эту вакансию")

            response = await uow.repository.create(response_in, user_id)
            await uow.commit()

            return response

    async def get_my_responses(self, current_user_id: int) -> Iterable[response_dto.Response]:
        """Получить все отклики текущего соискателя"""
        async with self.uow as uow:
            return await uow.repository.get_by_user_id(current_user_id)

    async def get_job_responses(self, job_id: int) -> Iterable[response_dto.Response]:
        """
        Получить все отклики на конкретную вакансию.
        *в роутере нужно будет проверить, является ли пользователь автором вакансии.*
        """
        async with self.uow as uow:
            return await uow.repository.get_by_job_id(job_id)

    async def delete_response(self, response_id: int, current_user_id: int) -> None:
        """Удаление отклика"""
        async with self.uow as uow:

            response = await uow.repository.retrieve(response_id)
            if not response:
                raise ValueError("Отклик не найден")

            if response.user_id != current_user_id:
                raise PermissionError("Вы не можете удалить чужой отклик")

            await uow.repository.delete(response_id)
            await uow.commit()
