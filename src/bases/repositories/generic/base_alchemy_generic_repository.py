from typing import Any, Generic, Optional, Tuple, Type, TypeVar

from bases import base_alchemy_model, base_dto
from bases.repositories import base_alchemy_repository
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql import expression
from storage.sqlalchemy import connection_proxy

T = TypeVar("T", bound=base_alchemy_model.Base)  # модель ORM # noqa
O = TypeVar("O", bound=base_dto.BaseDTO)  # Output модель # noqa
C = TypeVar("C", bound=base_dto.BaseDTO)  # Create DTO # noqa
U = TypeVar("U", bound=base_dto.BaseDTO)  # Update DTO # noqa


class BaseAlchemyGenericSyncRepository(
    base_alchemy_repository.BaseAlchemySyncRepository, Generic[T, O, C, U]
):
    """
    Базовый синхронный репозиторий с унифицированными CRUD операциями

    :param connection_proxy_: Прокси для синхронного подключения к БД
    :type connection_proxy_: connection_proxy.AlchemySyncConnectionProxy
    """

    alchemy_model: Type[T]
    output_model: Type[O]

    def __init__(self, connection_proxy_: connection_proxy.AlchemySyncConnectionProxy) -> None:
        super().__init__(connection_proxy_)

    def create(self, data: C) -> O:
        """
        Создает новый объект в БД

        :param data: Данные для создания объекта
        :return: Созданный объект
        """

        session = self.connection_proxy.connect()
        db_obj = self.alchemy_model(**data.model_dump())
        session.add(db_obj)
        session.flush()
        return self.output_model.model_validate(db_obj)

    def retrieve(self, *conditions: expression.ColumnElement[bool], **filters: Any) -> Optional[O]:
        """
        Получает один объект из БД по условиям

        :param conditions: Условия фильтрации
        :param filters: Параметры фильтрации
        :return: Найденный объект или None
        """

        session = self.connection_proxy.connect()
        execution_result = self._filter_by(session, *conditions, **filters)
        db_obj = execution_result.scalars().first()
        return self.output_model.model_validate(db_obj) if db_obj else None

    def list(
        self,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        *conditions: expression.ColumnElement[bool],
        **filters: Any,
    ) -> list[O]:
        """
        Получает список объектов из БД с возможностью пагинации и фильтрации

        :param limit: Максимальное количество объектов
        :param skip: Количество пропускаемых объектов
        :param conditions: Условия фильтрации
        :param filters: Параметры фильтрации
        :return: Список объектов
        """
        if limit is not None:
            filters["limit"] = limit
        if skip is not None:
            filters["skip"] = skip

        session = self.connection_proxy.connect()
        execution_result = self._filter_by(session, *conditions, **filters)
        return [self.output_model.model_validate(obj) for obj in execution_result.scalars()]

    def update(self, data: U, *conditions: expression.ColumnElement[bool], **filters: Any) -> O:
        """
        Обновляет объект в БД

        :param data: Данные для обновления
        :return: Обновленный объект
        :raises ValueError: Если объект не найден
        """
        session = self.connection_proxy.connect()
        execution_result = self._filter_by(session, *conditions, **filters)
        db_obj = execution_result.scalars().first()
        if not db_obj:
            raise ValueError("Объект не найден")

        update_data = data.model_dump(exclude_unset=False, exclude_none=False)

        # Обновляем только те поля, которые явно переданы в DTO
        for key, value in update_data.items():
            if key in data.model_fields_set:
                setattr(db_obj, key, value)

        session.flush()
        return self.output_model.model_validate(db_obj)

    def delete(self, *conditions: expression.ColumnElement[bool], **filters: Any) -> None:
        """
        Удаляет объект из БД

        :param conditions: Условия фильтрации
        :param filters: Параметры фильтрации
        :raises ValueError: Если объект не найден
        """

        session = self.connection_proxy.connect()
        execution_result = self._filter_by(session, *conditions, **filters)
        db_obj = execution_result.scalars().first()
        if not db_obj:
            raise ValueError("Объект не найден")
        session.delete(db_obj)
        session.flush()

    def _filter_by(
        self, session: Session, *conditions: expression.ColumnElement[bool], **filters: Any
    ) -> Result[Tuple[Any]]:
        """
        Внутренний метод для фильтрации объектов

        :param session: Сессия SQLAlchemy
        :param limit: Лимит выборки
        :param skip: Смещение выборки
        :param conditions: Условия фильтрации
        :param filters: Параметры фильтрации
        :return: Результат выполнения запроса
        """

        # Извлекаем параметры пагинации
        limit = filters.pop("limit", None)
        skip = filters.pop("skip", None)

        query = select(self.alchemy_model)
        if conditions:
            query = query.filter(*conditions)
        if filters:
            query = query.filter_by(**filters)

        if skip is not None:
            query = query.offset(skip)
        if limit is not None:
            query = query.limit(limit)

        return session.execute(query)


class BaseAlchemyGenericAsyncRepository(
    base_alchemy_repository.BaseAlchemyAsyncRepository, Generic[T, O, C, U]
):
    """
    Базовый асинхронный репозиторий с унифицированными CRUD операциями

    :param connection_proxy_: Прокси для асинхронного подключения к БД
    :type connection_proxy_: connection_proxy.AlchemyAsyncConnectionProxy

    Атрибуты класса:
        alchemy_model: ORM модель SQLAlchemy
        output_model: Модель DTO для возврата данных
    """

    alchemy_model: Type[T]
    output_model: Type[O]

    def __init__(self, connection_proxy_: connection_proxy.AlchemyAsyncConnectionProxy) -> None:
        super().__init__(connection_proxy_)

    async def create(self, data: C) -> O:
        """
        Создает новый объект в БД

        :param data: Данные для создания объекта
        :return: Созданный объект
        """

        session = await self.connection_proxy.connect()
        db_obj = self.alchemy_model(**data.model_dump())
        session.add(db_obj)
        await session.flush()
        return self.output_model.model_validate(db_obj)

    async def retrieve(
        self, *conditions: expression.ColumnElement[bool], **filters: Any
    ) -> Optional[O]:
        """
        Получает один объект из БД по условиям

        :param conditions: Условия фильтрации
        :param filters: Параметры фильтрации
        :return: Найденный объект или None
        """

        session = await self.connection_proxy.connect()
        execution_result = await self._filter_by(session, *conditions, **filters)
        db_obj = execution_result.scalars().first()
        return self.output_model.model_validate(db_obj) if db_obj else None

    async def list(
        self,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        *conditions: expression.ColumnElement[bool],
        **filters: Any,
    ) -> list[O]:
        """
        Получает список объектов из БД с возможностью пагинации и фильтрации

        :param limit: Максимальное количество объектов
        :param skip: Количество пропускаемых объектов
        :param conditions: Условия фильтрации
        :param filters: Параметры фильтрации
        :return: Список объектов
        """
        if limit is not None:
            filters["limit"] = limit
        if skip is not None:
            filters["skip"] = skip

        session = await self.connection_proxy.connect()
        execution_result = await self._filter_by(session, *conditions, **filters)
        return [self.output_model.model_validate(obj) for obj in execution_result.scalars()]

    async def update(
        self, data: U, *conditions: expression.ColumnElement[bool], **filters: Any
    ) -> O:
        """
        Обновляет объект в БД

        :param data: Данные для обновления
        :return: Обновленный объект
        :raises ValueError: Если объект не найден
        """
        session = await self.connection_proxy.connect()
        execution_result = await self._filter_by(session, *conditions, **filters)
        db_obj = execution_result.scalars().first()
        if not db_obj:
            raise ValueError("Объект не найден")

        update_data = data.model_dump(exclude_unset=False, exclude_none=False)

        # Обновляем только те поля, которые явно переданы в DTO
        for key, value in update_data.items():
            if key in data.model_fields_set:
                setattr(db_obj, key, value)

        await session.flush()
        return self.output_model.model_validate(db_obj)

    async def delete(self, *conditions: expression.ColumnElement[bool], **filters: Any) -> None:
        """
        Удаляет объект из БД

        :param conditions: Условия фильтрации
        :param filters: Параметры фильтрации
        :raises ValueError: Если объект не найден
        """

        session = await self.connection_proxy.connect()
        execution_result = await self._filter_by(session, *conditions, **filters)
        db_obj = execution_result.scalars().first()
        if not db_obj:
            raise ValueError("Объект не найден")
        await session.delete(db_obj)
        await session.flush()

    async def _filter_by(
        self, session: AsyncSession, *conditions: expression.ColumnElement[bool], **filters: Any
    ) -> Result[Tuple[Any]]:
        """
        Внутренний метод для фильтрации объектов

        :param session: Сессия SQLAlchemy
        :param limit: Лимит выборки
        :param skip: Смещение выборки
        :param conditions: Условия фильтрации
        :param filters: Параметры фильтрации
        :return: Результат выполнения запроса
        """

        # Извлекаем параметры пагинации
        limit = filters.pop("limit", None)
        skip = filters.pop("skip", None)

        query = select(self.alchemy_model)
        if conditions:
            query = query.filter(*conditions)
        if filters:
            query = query.filter_by(**filters)

        if skip is not None:
            query = query.offset(skip)
        if limit is not None:
            query = query.limit(limit)

        return await session.execute(query)
