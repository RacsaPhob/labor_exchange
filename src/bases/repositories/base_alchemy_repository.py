from typing import Any, Generic, Iterable, TypeVar

from bases.repositories import base_repository
from storage.sqlalchemy import connection_proxy

OutputModel = TypeVar("OutputModel")


class BaseAlchemySyncRepository(base_repository.BaseSyncRepository, Generic[OutputModel]):
    """
    Базовый класс репозитория для Алхимии
    """

    def __init__(self, connection_proxy_: connection_proxy.AlchemySyncConnectionProxy) -> None:
        """
        Инициализировать переменные
        :param connection_proxy_: объект прокси-соединения
        """
        self.connection_proxy = connection_proxy_

    def create(self, *args, **kwargs) -> OutputModel:
        """
        Создать запись
        """
        raise NotImplementedError()

    def retrieve(self, *args, **kwargs) -> OutputModel:
        """
        Получить запись
        """
        raise NotImplementedError()

    def list(self, *args, **kwargs) -> Iterable[OutputModel]:
        """
        Получить список записей
        """
        raise NotImplementedError()

    def update(self, *args, **kwargs) -> OutputModel:
        """
        Обновить запись
        """
        raise NotImplementedError()

    def delete(self, *args, **kwargs) -> Any:
        """
        Удалить запись
        """
        raise NotImplementedError()


class BaseAlchemyAsyncRepository(base_repository.BaseAsyncRepository, Generic[OutputModel]):
    """
    Базовый класс репозитория для Алхимии
    """

    def __init__(self, connection_proxy_: connection_proxy.AlchemyAsyncConnectionProxy) -> None:
        """
        Инициализировать переменные
        :param connection_proxy_: объект прокси-соединения
        """
        self.connection_proxy = connection_proxy_

    async def create(self, *args, **kwargs) -> OutputModel:
        """
        Создать запись
        """
        raise NotImplementedError()

    async def retrieve(self, *args, **kwargs) -> OutputModel | None:
        """
        Получить запись
        """
        raise NotImplementedError()

    async def list(self, *args, **kwargs) -> Iterable[OutputModel]:
        """
        Получить список записей
        """
        raise NotImplementedError()

    async def update(self, *args, **kwargs) -> OutputModel:
        """
        Обновить запись
        """
        raise NotImplementedError()

    async def delete(self, *args, **kwargs) -> Any:
        """
        Удалить запись
        """
        raise NotImplementedError()
