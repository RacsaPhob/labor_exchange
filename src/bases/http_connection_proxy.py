import httpx
from bases import base_proxy


class HTTPSyncSession(base_proxy.SyncConnectionProxy):
    """
    Синхронный клиент httpx
    """

    def __init__(self) -> None:
        """
        Инициализировать переменные
        """

        self._client = httpx.Client()

    def connect(self) -> httpx.Client:
        """
        Получить HTTP-клиент
        """

        return self._client

    def disconnect(self) -> None:
        """
        Отключить HTTP-клиент
        """

        self._client.close()


class HTTPAsyncSession(base_proxy.AsyncConnectionProxy):
    """
    Асинхронный клиент httpx
    """

    def __init__(self) -> None:
        """
        Инициализировать переменные
        """

        self._client = httpx.AsyncClient()

    async def connect(self, *args, **kwargs) -> httpx.AsyncClient:
        """
        Получить HTTP-клиент
        """

        return self._client

    async def disconnect(self, *args, **kwargs) -> None:
        """
        Отключить HTTP-клиент
        """

        await self._client.aclose()
