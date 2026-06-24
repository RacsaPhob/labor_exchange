from bases.repositories import http_repository
from bases.uows import base_uow


class BaseSyncHTTPUOW(base_uow.BaseSyncUOW):
    """
    Синхронный UOW для работы с синхронными HTTP-репозиториями
    """

    def __init__(self, repository: http_repository.SyncHTTPRepository):
        """
        Инициализировать переменные
        :param repository: синхронный репозиторий
        """

        self.repository = repository
        super().__init__()

    def commit(self) -> None:
        """
        Сделать коммит изменений
        """

        raise NotImplementedError()

    def rollback(self) -> None:
        """
        Закрыть сессию
        """

        self.repository.client.close()


class BaseAsyncHTTPUOW(base_uow.BaseAsyncUOW):
    """
    Асинхронный UOW для работы с асинхронными HTTP-репозиториями
    """

    def __init__(self, repository: http_repository.AsyncHTTPRepository):
        """
        Инициализировать переменные
        :param repository: асинхронный репозиторий
        """

        self.repository = repository
        super().__init__()

    async def commit(self) -> None:
        """
        Сделать коммит изменений
        """

        raise NotImplementedError()

    async def rollback(self) -> None:
        """
        Закрыть сессию
        """
        client = await self.repository._ensure_client()
        await client.aclose()
