from __future__ import annotations

from typing import Generic, Union
from unittest.mock import AsyncMock, MagicMock

from bases.repositories import base_alchemy_repository
from bases.repositories.generic import base_alchemy_generic_repository
from bases.repositories.generic.base_alchemy_generic_repository import C, O, T, U
from bases.uows import base_uow
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import SessionTransaction


class AlchemySyncGenericUOW(base_uow.BaseSyncUOW, Generic[T, O, C, U]):
    """
    UOW для работы с синхронными репозиториями Алхимии
    """

    def __init__(
        self,
        repository: base_alchemy_generic_repository.BaseAlchemyGenericSyncRepository[
            T, O, C, U
        ],  # noqa
    ) -> None:
        """
        Инициализировать переменные
        :param repository: синхронный репозиторий Алхимии
        """
        self._transaction: SessionTransaction | None = None
        self._is_transaction_commited = False
        self.repository = repository

    def __enter__(self) -> AlchemySyncGenericUOW[T, O, C, U]:  # noqa
        """
        Войти в контекстный менеджер
        :return: объект UOW
        """
        self._transaction = self.repository.connection_proxy.connect().begin()
        self._is_transaction_commited = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Сделать откат изменений
        """
        if exc_type is not None:  # Если было исключение
            self.rollback()
        else:
            self.repository.connection_proxy.disconnect()

    def commit(self) -> None:
        """
        Сделать коммит изменений
        """
        if self._transaction is None:
            raise ValueError("Объект транзакции не инициализирован!")

        self._transaction.commit()
        self._is_transaction_commited = True

    def rollback(self) -> None:
        """
        Сделать откат изменений
        """
        if self._transaction is None:
            raise ValueError("Объект транзакции не инициализирован!")

        if not self._is_transaction_commited:
            self._transaction.rollback()

        self.repository.connection_proxy.disconnect()


class AlchemyAsyncGenericUOW(base_uow.BaseAsyncUOW, Generic[T, O, C, U]):
    """
    UOW для работы с асинхронными репозиториями Алхимии
    """

    def __init__(
        self,
        repository: Union[
            base_alchemy_repository.BaseAlchemyAsyncRepository[O],
            base_alchemy_generic_repository.BaseAlchemyGenericAsyncRepository[T, O, C, U],  # noqa
        ],
    ) -> None:
        self._transaction: AsyncSession | None = None
        self._is_transaction_commited = False
        self.repository = repository

    async def __aenter__(self) -> AlchemyAsyncGenericUOW[T, O, C, U]:  # noqa
        """
        Войти в контекстный менеджер
        :return: объект UOW
        """
        self._transaction = await self.repository.connection_proxy.connect()
        if not self._transaction.in_transaction():
            await self._transaction.begin()
        self._is_transaction_commited = False
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Сделать откат изменений
        """
        if exc_type is not None:  # Если было исключение
            await self.rollback()
        else:
            await self.repository.connection_proxy.disconnect()

    async def commit(self) -> None:
        """
        Сделать коммит изменений
        """
        if self._transaction is None:
            raise ValueError("Объект транзакции не инициализирован!")

        await self._transaction.commit()
        self._is_transaction_commited = True

    async def rollback(self) -> None:
        """
        Сделать откат изменений
        """
        if self._transaction is None:
            raise ValueError("Объект транзакции не инициализирован!")

        if not self._is_transaction_commited:
            await self._transaction.rollback()

        await self.repository.connection_proxy.disconnect()


class TestAlchemySyncUOW(AlchemySyncGenericUOW[T, O, C, U], Generic[T, O, C, U]):
    """
    Тестовый UOW для синхронной реализации Алхимии
    """

    def __init__(
        self,
        repository: base_alchemy_generic_repository.BaseAlchemyGenericSyncRepository[
            T, O, C, U
        ],  # noqa
    ) -> None:
        """
        Инициализировать переменные
        :param repository: репозиторий
        """
        super().__init__(repository)
        self._session = self.repository.connection_proxy.connect()
        self.repository.connection_proxy.connect = MagicMock(side_effect=lambda: self._session)  # type: ignore[method-assign] # noqa

    def __enter__(self) -> TestAlchemySyncUOW[T, O, C, U]:  # noqa
        """
        Войти в контекстный менеджер
        :return: объект UOW
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Сделать откат изменений
        """
        if exc_type is not None:  # Если было исключение
            self.rollback()
        else:
            self.repository.connection_proxy.disconnect()

    def commit(self) -> None:
        """
        Сделать коммит изменений
        """
        self._session.commit()

    def rollback(self) -> None:
        """
        Сделать откат изменений
        """
        self._session.rollback()
        self.repository.connection_proxy.disconnect()


class TestAlchemyAsyncUOW(AlchemyAsyncGenericUOW[T, O, C, U], Generic[T, O, C, U]):
    """
    Тестовый UOW для асинхронной реализации Алхимии
    """

    def __init__(
        self,
        repository: base_alchemy_generic_repository.BaseAlchemyGenericAsyncRepository[
            T, O, C, U
        ],  # noqa
    ) -> None:
        """
        Инициализировать переменные
        :param repository: репозиторий
        """
        super().__init__(repository)

    async def __aenter__(self) -> TestAlchemyAsyncUOW[T, O, C, U]:  # noqa
        """
        Войти в контекстный менеджер
        :return: объект UOW
        """
        self._session = await self.repository.connection_proxy.connect()
        self.repository.connection_proxy.connect = AsyncMock(return_value=self._session)  # type: ignore[method-assign] # noqa
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Сделать откат изменений
        """
        if exc_type is not None:  # Если было исключение
            await self.rollback()
        else:
            await self.repository.connection_proxy.disconnect()

    async def commit(self) -> None:
        """
        Сделать коммит изменений
        """
        await self._session.commit()

    async def rollback(self) -> None:
        """
        Сделать откат изменений
        """
        await self._session.rollback()
        await self.repository.connection_proxy.disconnect()
