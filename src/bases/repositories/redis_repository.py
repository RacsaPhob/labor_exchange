from typing import Any, Callable, List, Optional, TypeVar

import redis
from bases.repositories import base_repository
from storage.redis import redis_connection

T = TypeVar("T")


class RedisErrorCatcherDecorator:
    """
    Класс, реализующий метод-декоратор для отлавливания ошибок в репозитории Redis
    """

    @staticmethod
    def _catch_sync_exception(method: Callable[..., T]) -> Callable[..., T]:
        """
        Отловить ошибку при синхронном запросе к бд Redis
        """

        def execute_method(self: Any, *args: Any, **kwargs: Any) -> T:
            try:
                return method(self, *args, **kwargs)
            except redis.RedisError as redis_error:
                raise redis_error
            except NotImplementedError as not_impl_error:
                raise not_impl_error

        return execute_method

    @staticmethod
    def _catch_async_exception(method: Callable[..., Any]) -> Callable[..., Any]:
        """
        Отловить ошибку при асинхронном запросе к бд Redis
        """

        async def execute_method(self: Any, *args: Any, **kwargs: Any) -> Any:
            try:
                return await method(self, *args, **kwargs)
            except redis.RedisError as redis_error:
                raise redis_error
            except NotImplementedError as not_impl_error:
                raise not_impl_error

        return execute_method

    catch_sync_exception = _catch_sync_exception
    catch_async_exception = _catch_async_exception


class SyncRedisRepository(base_repository.BaseSyncRepository):
    """
    Репозиторий для синхронной работы с кэшем
    """

    def __init__(self, connection: redis_connection.RedisConnection) -> None:
        self.connection = connection.get_connection()

    @RedisErrorCatcherDecorator.catch_sync_exception
    def create(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if ttl:
            self.connection.set(key, value, ex=ttl)
        else:
            self.connection.set(key, value)

    @RedisErrorCatcherDecorator.catch_sync_exception
    def retrieve(self, key: str) -> Optional[Any]:
        return self.connection.get(key)

    @RedisErrorCatcherDecorator.catch_sync_exception
    def list(self, *args: Any, **kwargs: Any) -> List[Any]:
        raise NotImplementedError("List method not implemented")

    @RedisErrorCatcherDecorator.catch_sync_exception
    def update(self, key: str, new_value: Any) -> None:
        self.connection.set(key, new_value)

    @RedisErrorCatcherDecorator.catch_sync_exception
    def delete(self, key: str) -> None:
        self.connection.delete(key)


class AsyncRedisRepository(base_repository.BaseAsyncRepository):
    """
    Репозиторий для асинхронной работы с кэшем
    """

    def __init__(self, connection: redis_connection.RedisAsyncConnection) -> None:
        self.connection = connection.get_connection()

    @RedisErrorCatcherDecorator.catch_async_exception
    async def create(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if ttl:
            await self.connection.set(key, value, ex=ttl)
        else:
            await self.connection.set(key, value)

    @RedisErrorCatcherDecorator.catch_async_exception
    async def retrieve(self, key: str) -> Optional[Any]:
        return await self.connection.get(key)

    @RedisErrorCatcherDecorator.catch_async_exception
    async def list(self, *args: Any, **kwargs: Any) -> List[Any]:
        raise NotImplementedError("List method not implemented")

    @RedisErrorCatcherDecorator.catch_async_exception
    async def update(self, key: str, new_value: Any) -> None:
        await self.connection.set(key, new_value)

    @RedisErrorCatcherDecorator.catch_async_exception
    async def delete(self, key: str) -> None:
        await self.connection.delete(key)
