from typing import Iterable
from sqlalchemy import select

from models.domain.responses import Response
from bases.repositories.base_alchemy_repository import BaseAlchemyAsyncRepository
from models.dto import response_dto


def _response_to_dto(response: Response) -> response_dto.Response:
    result = response_dto.Response(
        id=response.id,
        user_id=response.user_id,
        job_id=response.job_id,
        message=response.message
    )
    return result


def _scalars_to_dto_list(scalars: Iterable[Response]) -> Iterable[response_dto.Response]:
    responses = []
    for response in scalars:
        responses.append(_response_to_dto(response))
    return responses


class ResponseRepository(BaseAlchemyAsyncRepository[Response]):
    async def create(self, response: response_dto.ResponseCreate, user_id: int) -> response_dto.Response:
        """
            Создать новый отклик на вакансию
            :param response: DTO с данными отклика (сообщение, job_id)
            :param user_id: ID текущего пользователя
        """
        response_db = Response(
            user_id=user_id,
            job_id=response.job_id,
            message=response.message
        )
        session = await self.connection_proxy.connect()
        session.add(response_db)
        await session.flush()

        return _response_to_dto(response_db)

    async def retrieve(self, response_id: int) -> response_dto.Response | None:
        """Получить отклик по ID"""
        session = await self.connection_proxy.connect()
        response = await session.get(entity=Response, ident=response_id)
        if response:
            return _response_to_dto(response)
        else:
            return None

    async def retrieve_by_user_id_and_job_id(self, user_id: int, job_id: int) -> response_dto.Response | None:
        """Получить отклик определенного пользователя на определенную вакансию"""
        session = await self.connection_proxy.connect()
        stmt = select(Response).where(Response.user_id == user_id, Response.job_id == job_id)
        result = await session.execute(stmt)
        response = result.scalar_one_or_none()
        if response:
            return _response_to_dto(response)
        else:
            return None

    async def list(self) -> Iterable[response_dto.Response]:
        """Получить все отклики"""
        stmt = select(Response)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        responses = _scalars_to_dto_list(result.scalars().all())
        return responses

    async def update(self, response_id: int, response_update: response_dto.ResponseUpdate) -> response_dto.Response | None:
        """
            Обновить отклик
            :param response_id: ID отклика для обновления
            :param response_update: DTO с новыми данными (сообщением)
        """
        session = await self.connection_proxy.connect()

        response = await session.get(Response, response_id)
        if not response:
            return None

        response.message = response_update.message
        await session.flush()

        return _response_to_dto(response)

    async def delete(self, response_id: int) -> None:
        """Удалить отклик"""
        session = await self.connection_proxy.connect()

        response = await session.get(entity=Response, ident=response_id)
        if response:
            await session.delete(response)

    async def get_by_job_id(self, job_id: int) -> Iterable[response_dto.Response]:
        """Получить все отклики на конкретную вакансию."""
        stmt = select(Response).where(Response.job_id == job_id)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        responses = _scalars_to_dto_list(result.scalars().all())
        return responses

    async def get_by_user_id(self, user_id: int) -> Iterable[Response]:
        """Получить все отклики конкретного пользователя."""
        stmt = select(Response).where(Response.user_id == user_id)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        responses = _scalars_to_dto_list(result.scalars().all())
        return responses

    async def check_exists(self, user_id: int, job_id: int) -> bool:
        """Проверить, откликался ли уже этот пользователь на эту вакансию."""
        stmt = select(Response).where(Response.user_id == user_id, Response.job_id == job_id)
        session = await self.connection_proxy.connect()
        result = await session.execute(stmt)
        return result.first() is not None
