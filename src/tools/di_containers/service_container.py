from dependency_injector import containers, providers

from tools.factories.alchemy_engine_factory import AlchemyAsyncEngineFactory
from storage.sqlalchemy.connection_proxy import AlchemyAsyncConnectionProxy

from repositories.user_repository import UserRepository
from bases.uows.user_uow import UserUOW
from services.user_service import UserService

from repositories.job_repository import JobRepository
from bases.uows.job_uow import JobUOW
from services.job_service import JobService

from repositories.response_repository import ResponseRepository
from bases.uows.response_uow import ResponseUOW
from services.response_service import ResponseService


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    db_engine_factory = providers.Singleton(
        AlchemyAsyncEngineFactory,
        dsn=config.db.dsn,
        max_size=config.db.max_size
    )

    db_proxy = providers.Singleton(
        AlchemyAsyncConnectionProxy,
        engine_factory=db_engine_factory
    )

    user_repository = providers.Factory(
        UserRepository,
        connection_proxy_=db_proxy
    )

    job_repository = providers.Factory(
        JobRepository,
        connection_proxy_=db_proxy
    )

    response_repository = providers.Factory(
        ResponseRepository,
        connection_proxy_=db_proxy
    )

    user_uow = providers.Factory(
        UserUOW,
        repository=user_repository
    )

    job_uow = providers.Factory(
        JobUOW,
        repository=job_repository
    )

    response_uow = providers.Factory(
        ResponseUOW,
        repository=response_repository
    )

    user_service = providers.Factory(
        UserService,
        uow=user_uow
    )

    job_service = providers.Factory(
        JobService,
        uow=job_uow,
        user_service=user_service
    )

    response_service = providers.Factory(
        ResponseService,
        uow=response_uow,
        user_service=user_service
    )
