from bases.uows.base_alchemy_uow import BaseAlchemyAsyncUOW
from repositories.job_repository import JobRepository


class JobUOW(BaseAlchemyAsyncUOW[JobRepository]):
    pass
