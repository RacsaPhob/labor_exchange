import asyncio
import time
from typing import Optional
from unittest.mock import MagicMock

from bases import base_proxy
from config import app_config, pg_config
from sqlalchemy import Engine, create_engine, inspect
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker
from tools.factories import alchemy_engine_factory

app_config_ = app_config.app_config
pg_config_ = pg_config.pg_config


class AlchemySyncConnectionProxyBase(base_proxy.SyncConnectionProxy):
    """
    Базовое прокси-соединение для Алхимии
    """

    def __init__(
        self,
        engine_factory: alchemy_engine_factory.AlchemySyncEngineFactory,
    ) -> None:
        """
        Инициализировать переменные
        """
        self._session_maker: Optional[sessionmaker] = None
        self._session: Optional[Session] = None

        self._engine = engine_factory.create()

    def connect(self) -> Session:
        """
        Получить сессию БД
        :return: сессия
        """
        raise NotImplementedError()

    def disconnect(self) -> None:
        """
        Разорвать соединение с БД
        """
        raise NotImplementedError()


class AlchemyAsyncConnectionProxyBase(base_proxy.AsyncConnectionProxy):
    """
    Базовое прокси-соединение для Алхимии
    """

    def __init__(
        self,
        engine_factory: alchemy_engine_factory.AlchemyAsyncEngineFactory,
    ) -> None:
        """
        Инициализировать переменные
        """
        self._session_maker: Optional[async_sessionmaker] = None  # Теперь instance-переменная
        self._session: Optional[AsyncSession] = None
        self._engine = engine_factory.create()

    async def connect(self) -> AsyncSession:
        """
        Получить сессию БД
        :return: сессия
        """
        raise NotImplementedError()

    async def disconnect(self) -> None:
        """
        Разорвать соединение с БД
        """
        raise NotImplementedError()


class AlchemySyncConnectionProxy(AlchemySyncConnectionProxyBase):
    """
    Синхронное прокси-соединение для Алхимии
    """

    def _connect(self, engine: Engine) -> None:
        if self._session_maker is None:
            self._session_maker = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine,
                expire_on_commit=False,
            )

        if self._session is None:
            self._session = self._session_maker()

    def connect(self) -> Session:
        self._connect(self._engine)
        if self._session is None:
            raise ValueError("Session was not created")
        return self._session

    def disconnect(self) -> None:
        """
        Закрыть сессию и соединение.
        """
        if self._session:
            self._session.close()
            self._session = None
        self._session_maker = None


class AlchemyAsyncConnectionProxy(AlchemyAsyncConnectionProxyBase):
    """
    Асинхронное прокси-соединение для Алхимии
    """

    async def _connect(self, engine: AsyncEngine) -> None:
        if self._session_maker is None:
            self._session_maker = async_sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
        if self._session is None:
            self._session = self._session_maker()

    async def connect(self) -> AsyncSession:
        await self._connect(self._engine)
        if self._session is None:
            raise ValueError("Session was not created")
        return self._session

    async def disconnect(self) -> None:
        """
        Закрыть сессию и соединение.
        """
        if self._session:
            await self._session.close()
            self._session = None
        self._session_maker = None


class AlchemyTestSyncConnectionProxy(AlchemySyncConnectionProxyBase):
    """
    Класс синхронного прокси-подключения для тестов
    """

    def __init__(
        self,
        engine_factory: alchemy_engine_factory.AlchemySyncEngineFactory,
    ) -> None:
        """
        Инициализировать переменные
        """
        super().__init__(engine_factory)

        self._engine = create_engine(
            str(pg_config_.postgres_dsn), pool_size=pg_config_.connection_pool_size, echo=True
        )
        self._session_maker = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
            class_=Session,
            expire_on_commit=False,
        )

    def _mock(self) -> None:
        """
        Сделать моковое взаимодействие с БД
        """
        if self._session is None:
            return

        deletion = self._session.delete

        def mock_delete(instance):
            insp = inspect(instance)

            if not insp.persistent:
                self._session.expunge(instance)
            else:
                deletion(instance)

            return time.sleep(0)

        self._session.commit = MagicMock(side_effect=self._session.flush)  # type: ignore[method-assign] # noqa
        self._session.delete = MagicMock(side_effect=mock_delete)  # type: ignore[method-assign] # noqa

    def connect(self) -> Session:
        """
        Получить сессию БД
        :return: асинхронная сессия
        """
        if self._session_maker is None:
            raise ValueError("SessionMaker is not set")

        self._session = self._session_maker()
        self._mock()
        assert self._session is not None
        return self._session

    def disconnect(self) -> None:
        """
        Разорвать соединение с БД
        """
        if self._session:
            self._session.close()
        self._engine.dispose()


class AlchemyTestAsyncConnectionProxy(AlchemyAsyncConnectionProxyBase):
    """
    Класс асинхронного прокси-подключения для тестов
    """

    def __init__(
        self,
        engine_factory: alchemy_engine_factory.AlchemyAsyncEngineFactory,
    ) -> None:
        """
        Инициализировать переменные
        """
        super().__init__(engine_factory)

        self._engine = create_async_engine(
            str(pg_config_.postgres_async_dsn), pool_size=pg_config_.connection_pool_size, echo=True
        )
        self._session_maker = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    def _mock(self) -> None:
        """
        Сделать моковое взаимодействие с БД
        """
        if self._session is None:
            return

        deletion = self._session.delete

        async def mock_delete(instance):
            insp = inspect(instance)

            if not insp.persistent:
                self._session.expunge(instance)
            else:
                await deletion(instance)

            return await asyncio.sleep(0)

        self._session.commit = MagicMock(side_effect=self._session.flush)  # type: ignore[method-assign] # noqa
        self._session.delete = MagicMock(side_effect=mock_delete)  # type: ignore[method-assign] # noqa

    async def connect(self) -> AsyncSession:
        """
        Получить сессию БД
        :return: асинхронная сессия
        """
        if self._session_maker is None:
            raise ValueError("SessionMaker is not set")

        self._session = self._session_maker()
        self._mock()
        assert self._session is not None
        return self._session

    async def disconnect(self) -> None:
        """
        Разорвать соединение с БД
        """
        if self._session:
            await self._session.close()
        await self._engine.dispose()
