from bases.repositories import redis_repository
from bases.uows import base_uow


class BaseSyncRedisUOW(base_uow.BaseSyncUOW):
    """
    Синхронный UOW для работы с синхронными Redis-репозиториями
    """

    def __init__(self, repository: redis_repository.SyncRedisRepository):
        """
        Инициализировать переменные
        :param repository: синхронный репозиторий Redis
        """
        self.repository = repository
        super().__init__()

    def __exit__(self, *args, **kwargs) -> None:
        """
        Выйти из контекстного менеджера
        """

        self.repository.connection.close()

    def commit(self) -> None:
        """
        Сделать коммит изменений
        """

        raise NotImplementedError()

    def rollback(self) -> None:
        """
        Сделать откат изменений
        """

        raise NotImplementedError()


class BaseAsyncRedisUOW(base_uow.BaseAsyncUOW):
    """
    Асинхронный UOW для работы с асинхронными Redis-репозиториями
    """

    def __init__(self, repository: redis_repository.AsyncRedisRepository):
        """
        Инициализировать переменные
        :param repository: асинхронный репозиторий Redis
        """
        self.repository = repository
        super().__init__()

    async def __aexit__(self, *args, **kwargs) -> None:
        """
        Выйти из контекстного менеджера
        """

        await self.repository.connection.aclose()

    async def commit(self) -> None:
        """
        Сделать коммит изменений
        """

        raise NotImplementedError()

    async def rollback(self) -> None:
        """
        Сделать откат изменений
        """

        raise NotImplementedError()
