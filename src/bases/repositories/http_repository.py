import json.decoder
import logging
from typing import Any, Callable, Coroutine, Iterable, Optional, TypeVar

import httpx
from bases import http_connection_proxy
from bases.repositories import base_repository
from models.dto import http_dto

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=base_repository.BaseSyncRepository)
A = TypeVar("A", bound=base_repository.BaseAsyncRepository)


class ResponseHandlerDecorator:
    """
    Класс, реализующий метод-декоратор для обработки HTTP-ответа
    """

    @staticmethod
    def _handle_sync(
        http_method: Callable[[T, http_dto.HTTPRequestDTO], httpx.Response],
    ) -> Callable[[T, http_dto.HTTPRequestDTO], http_dto.HTTPResponseDTO]:
        """
        Обработать синхронный http-запрос
        """

        def execute_method(
            self: T, request_params: http_dto.HTTPRequestDTO
        ) -> http_dto.HTTPResponseDTO:
            try:
                response = http_method(self, request_params)
            except httpx.HTTPError as http_error:
                raise http_error
            except Exception as exception:
                raise exception

            try:
                payload = response.json()
            except json.decoder.JSONDecodeError as error:
                logger.error(str(error))
                payload = None

            return http_dto.HTTPResponseDTO(
                status=response.status_code, headers=dict(response.headers), payload=payload
            )

        return execute_method

    @staticmethod
    def _handle_async(
        http_method: Callable[[A, http_dto.HTTPRequestDTO], Coroutine[Any, Any, httpx.Response]],
    ) -> Callable[[A, http_dto.HTTPRequestDTO], Coroutine[Any, Any, http_dto.HTTPResponseDTO]]:
        """
        Обработать асинхронный http-запрос
        """

        async def execute_method(
            self: A, request_params: http_dto.HTTPRequestDTO
        ) -> http_dto.HTTPResponseDTO:
            try:
                response = await http_method(self, request_params)
            except httpx.HTTPError as http_error:
                raise http_error
            except Exception as exception:
                raise exception

            try:
                payload = response.json()
            except json.decoder.JSONDecodeError as error:
                logger.error(str(error))
                payload = None

            return http_dto.HTTPResponseDTO(
                status=response.status_code, headers=dict(response.headers), payload=payload
            )

        return execute_method

    handle_sync = _handle_sync
    handle_async = _handle_async


class SyncHTTPRepository(base_repository.BaseSyncRepository):
    """
    Репозиторий для синхронных HTTP-запросов
    """

    def __init__(self, http_client: http_connection_proxy.HTTPSyncSession) -> None:
        """
        Инициализировать переменные
        :param http_client: HTTP-клиент
        """
        self.client = http_client.connect()

    @ResponseHandlerDecorator.handle_sync
    def create(self, request_params: http_dto.HTTPRequestDTO) -> httpx.Response:
        """
        Сделать POST-запрос
        :param request_params: параметры запроса
        :return: результаты запроса
        """
        return self.client.post(
            url=request_params.url,
            headers=request_params.headers,
            params=request_params.query_params,
            files=request_params.files,
            json=request_params.payload,
            data=request_params.form_data,
        )

    @ResponseHandlerDecorator.handle_sync
    def retrieve(self, request_params: http_dto.HTTPRequestDTO) -> httpx.Response:
        """
        Сделать GET-запрос
        :param request_params: параметры запроса
        :return: результаты запроса
        """
        return self.client.get(
            url=request_params.url,
            headers=request_params.headers,
            params=request_params.query_params,
        )

    def list(self, *args: Any, **kwargs: Any) -> Iterable[Any]:
        """
        Получить список записей
        """
        raise NotImplementedError("List method not implemented")

    @ResponseHandlerDecorator.handle_sync
    def update(self, request_params: http_dto.HTTPRequestDTO) -> httpx.Response:
        """
        Сделать PATCH-запрос
        :param request_params: параметры запроса
        :return: результаты запроса
        """
        return self.client.patch(
            url=request_params.url,
            headers=request_params.headers,
            params=request_params.query_params,
            json=request_params.payload,
            data=request_params.form_data,
        )

    @ResponseHandlerDecorator.handle_sync
    def delete(self, request_params: http_dto.HTTPRequestDTO) -> httpx.Response:
        """
        Сделать DELETE-запрос
        :param request_params: параметры запроса
        :return: результаты запроса
        """
        return self.client.delete(
            url=request_params.url,
            headers=request_params.headers,
            params=request_params.query_params,
        )


class AsyncHTTPRepository(base_repository.BaseAsyncRepository):
    """
    Репозиторий для асинхронных HTTP-запросов
    """

    def __init__(self, http_client: http_connection_proxy.HTTPAsyncSession) -> None:
        self._http_client = http_client
        self._client: Optional[httpx.AsyncClient] = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Убедиться, что клиент подключен"""
        if self._client is None:
            self._client = await self._http_client.connect()
        return self._client

    @ResponseHandlerDecorator.handle_async
    async def create(self, request_params: http_dto.HTTPRequestDTO) -> httpx.Response:
        """
        Сделать POST-запрос
        :param request_params: параметры запроса
        :return: результаты запроса
        """
        client = await self._ensure_client()

        return await client.post(
            url=request_params.url,
            headers=request_params.headers,
            params=request_params.query_params,
            json=request_params.payload,
            files=request_params.files,
            data=request_params.form_data,
        )

    @ResponseHandlerDecorator.handle_async
    async def retrieve(self, request_params: http_dto.HTTPRequestDTO) -> httpx.Response:
        """
        Сделать GET-запрос
        :param request_params: параметры запроса
        :return: результаты запроса
        """
        client = await self._ensure_client()

        return await client.get(
            url=request_params.url,
            headers=request_params.headers,
            params=request_params.query_params,
        )

    async def list(self, *args: Any, **kwargs: Any) -> Iterable[Any]:
        """
        Получить список записей
        """
        raise NotImplementedError("List method not implemented")

    @ResponseHandlerDecorator.handle_async
    async def update(self, request_params: http_dto.HTTPRequestDTO) -> httpx.Response:
        """
        Сделать PATCH-запрос
        :param request_params: параметры запроса
        :return: результаты запроса
        """
        client = await self._ensure_client()

        return await client.patch(
            url=request_params.url,
            headers=request_params.headers,
            params=request_params.query_params,
            json=request_params.payload,
            data=request_params.form_data,
        )

    @ResponseHandlerDecorator.handle_async
    async def delete(self, request_params: http_dto.HTTPRequestDTO) -> httpx.Response:
        """
        Сделать DELETE-запрос
        :param request_params: параметры запроса
        :return: результаты запроса
        """
        client = await self._ensure_client()

        return await client.delete(
            url=request_params.url,
            headers=request_params.headers,
            params=request_params.query_params,
        )
