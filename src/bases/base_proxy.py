import abc
from typing import Any


class SyncConnectionProxy(abc.ABC):
    """
    Proxy для подключения к удаленным ресурсам
    """

    @abc.abstractmethod
    def connect(self, *args, **kwargs) -> Any:
        """
        Подключиться к ресурсу
        """

        raise NotImplementedError()

    @abc.abstractmethod
    def disconnect(self, *args, **kwargs) -> Any:
        """
        Отключиться от ресурса
        """

        raise NotImplementedError()


class AsyncConnectionProxy(abc.ABC):
    """
    Proxy для подключения к удаленным ресурсам
    """

    @abc.abstractmethod
    async def connect(self, *args, **kwargs) -> Any:
        """
        Подключиться к ресурсу
        """

        raise NotImplementedError()

    @abc.abstractmethod
    async def disconnect(self, *args, **kwargs) -> Any:
        """
        Отключиться от ресурса
        """

        raise NotImplementedError()
