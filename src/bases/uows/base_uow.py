from __future__ import annotations  # noqa

import abc


class BaseSyncUOW(abc.ABC):
    """
    Абстрактный класс синхронного UOW
    """

    def __enter__(self, *args, **kwargs) -> BaseSyncUOW:
        """
        Войти в контекстный менеджер
        """

        return self

    def __exit__(self, *args, **kwargs) -> None:
        """
        Выйти из контекстного менеджера
        """

        self.rollback()

    @abc.abstractmethod
    def commit(self) -> None:
        """
        Сделать коммит изменений
        """

        raise NotImplementedError()

    @abc.abstractmethod
    def rollback(self) -> None:
        """
        Сделать откат изменений
        """

        raise NotImplementedError()


class BaseAsyncUOW(abc.ABC):
    """
    Абстрактный класс асинхронного UOW
    """

    async def __aenter__(self, *args, **kwargs) -> BaseAsyncUOW:
        """
        Войти в контекстный менеджер
        """

        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        """
        Выйти из контекстного менеджера
        """

        await self.rollback()

    @abc.abstractmethod
    async def commit(self) -> None:
        """
        Сделать коммит изменений
        """

        raise NotImplementedError()

    @abc.abstractmethod
    async def rollback(self) -> None:
        """
        Сделать откат изменений
        """

        raise NotImplementedError()
