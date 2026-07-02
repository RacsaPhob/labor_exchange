import bcrypt
from bases.services.base_service import BaseService
from bases.uows.user_uow import UserUOW
from models.dto import user_dto


class UserService(BaseService):

    def __init__(self, uow: UserUOW) -> None:
        self.uow = uow

    def _hash_password(self, password: str) -> str:
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(pwd_bytes, salt)

        return hashed_password.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Сравнивает чистый пароль с хешем из базы данных."""
        password_bytes = plain_password.encode('utf-8')
        hashed_password_bytes = hashed_password.encode('utf-8')

        return bcrypt.checkpw(password_bytes, hashed_password_bytes)

    async def register_user(self, user_in: user_dto.UserCreate) -> user_dto.UserResponse:
        """Регистрация нового пользователя"""
        async with self.uow as uow:
            existing_user = await uow.repository.get_by_email(user_in.email)
            if existing_user:
                raise ValueError("Пользователь с таким email уже существует")

            user_in.password = self._hash_password(user_in.password)

            new_user_model = await uow.repository.create(user_in)
            await uow.commit()

            return new_user_model

    async def get_user_by_id(self, user_id: int) -> user_dto.UserResponse:
        """Получение пользователя по ID"""
        async with self.uow as uow:
            user = await uow.repository.retrieve(user_id)
            if not user:
                raise ValueError("Пользователь не найден")

            return user

    async def get_user_by_email(self, email: str) -> user_dto.UserResponse:
        """Получение пользователя по email."""
        async with self.uow as uow:
            user = await uow.repository.get_by_email(email)
            if not user:
                raise ValueError("Пользователь с таким email не найден")

            return user

    async def authenticate_user(self, email: str, password: str) -> user_dto.UserResponse | None:
        """Аутентификация пользователя. Возвращает DTO, если всё верно, иначе None."""
        async with self.uow as uow:
            user = await uow.repository.get_by_email(email)
            if not user:
                return None

            if not self.verify_password(password, user.hashed_password):
                return None

            return user_dto.UserResponse.model_validate(user)
