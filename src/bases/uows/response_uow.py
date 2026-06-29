from bases.uows.base_alchemy_uow import BaseAlchemyAsyncUOW
from repositories.response_repository import ResponseRepository


class ResponseUOW(BaseAlchemyAsyncUOW[ResponseRepository]):
    pass
