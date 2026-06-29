from typing import List

from bases.services.base_service import BaseService
from bases.uows.response_uow import ResponseUOW
from models.dto import response_dto


class ResponseService(BaseService):

    def __init__(self, uow: ResponseUOW) -> None:
        self.uow = uow

    async def create_response(self, current_user_id: int,
                              response_in: response_dto.ResponseCreate) -> response_dto.ResponseOut:
        """Создание нового отклика"""

        async with self.uow as uow:
            already_exists = await uow.repository.check_exists(current_user_id, response_in.job_id)
            if already_exists:
                raise ValueError("Вы уже откликались на эту вакансию")

            response_data = response_in.model_dump()
            response_data["user_id"] = current_user_id

            new_response_model = await uow.repository.create(response_data)
            await uow.commit()

            return response_dto.ResponseOut.model_validate(new_response_model)

    async def get_my_responses(self, current_user_id: int) -> List[response_dto.ResponseOut]:
        """Получить все отклики текущего соискателя"""
        async with self.uow as uow:
            responses_models = await uow.repository.get_by_user_id(current_user_id)
            return [response_dto.ResponseOut.model_validate(r) for r in responses_models]

    async def get_job_responses(self, job_id: int) -> List[response_dto.ResponseOut]:
        """
        Получить все отклики на конкретную вакансию.
        *в роутере нужно будет проверить, является ли пользователь автором вакансии.*
        """
        async with self.uow as uow:
            responses_models = await uow.repository.get_by_job_id(job_id)
            return [response_dto.ResponseOut.model_validate(r) for r in responses_models]

    async def delete_response(self, response_id: int, current_user_id: int) -> None:
        """Удаление отклика"""
        async with self.uow as uow:

            response_model = await uow.repository.retrieve(response_id)
            if not response_model:
                raise ValueError("Отклик не найден")

            if response_model.user_id != current_user_id:
                raise PermissionError("Вы не можете удалить чужой отклик")

            await uow.repository.delete(response_id)
            await uow.commit()
