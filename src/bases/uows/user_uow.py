from bases.uows.base_alchemy_uow import BaseAlchemyAsyncUOW
from repositories.user_repository import UserRepository


class UserUOW(BaseAlchemyAsyncUOW[UserRepository]):
    pass