# stdlib
import abc
from typing import Any, AsyncIterator, Iterable


class BaseSyncRepository(abc.ABC):
    """
    Базовый класс репозитория
    """

    @abc.abstractmethod
    def create(self, *args, **kwargs) -> Any:
        """
        Создать запись
        """

        raise NotImplementedError

    @abc.abstractmethod
    def retrieve(self, *args, **kwargs) -> Any:
        """
        Получить запись
        """

        raise NotImplementedError

    @abc.abstractmethod
    def list(self, *args, **kwargs) -> Iterable:
        """
        Получить список записей
        """

        raise NotImplementedError

    @abc.abstractmethod
    def update(self, *args, **kwargs) -> Any:
        """
        Обновить запись
        """

        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, *args, **kwargs) -> Any:
        """
        Удалить запись
        """

        raise NotImplementedError


class BaseAsyncRepository(abc.ABC):
    """
    Базовый класс репозитория
    """

    @abc.abstractmethod
    async def create(self, *args, **kwargs) -> Any:
        """
        Создать запись
        """

        raise NotImplementedError

    @abc.abstractmethod
    async def retrieve(self, *args, **kwargs) -> Any:
        """
        Получить запись
        """

        raise NotImplementedError

    @abc.abstractmethod
    async def list(self, *args, **kwargs) -> Iterable | AsyncIterator:
        """
        Получить список записей
        """

        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, *args, **kwargs) -> Any:
        """
        Обновить запись
        """

        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, *args, **kwargs) -> Any:
        """
        Удалить запись
        """

        raise NotImplementedError
