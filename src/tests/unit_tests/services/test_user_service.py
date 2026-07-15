from unittest.mock import MagicMock
import pytest
import datetime

from services.user_service import UserService
from services.exceptions import ObjectDoesntExistsException, ObjectExistsException
from models.dto.user_dto import UserResponse, UserCreate


@pytest.fixture
def expected_user():
    return UserResponse(
        id=1,
        email="test@example.com",
        username="string",
        is_company=False,
        created_at=datetime.datetime.today()
    )


@pytest.fixture
def create_user_dto():
    return UserCreate(
        email="test@example.com",
        username="string",
        is_company=False,
        password="password"
    )


@pytest.fixture
def auth_service():
    return UserService(uow=None)


class TestGetUserById:
    """Тесты для метода get_user_by_id"""

    async def test_success(self, mock_uow, expected_user):
        mock_uow.repository.retrieve.return_value = expected_user
        service = UserService(uow=mock_uow)

        result = await service.get_user_by_id(user_id=1)

        assert result == expected_user
        mock_uow.repository.retrieve.assert_awaited_once_with(1)

    async def test_not_found(self, mock_uow):
        mock_uow.repository.retrieve.return_value = None
        service = UserService(uow=mock_uow)

        with pytest.raises(ObjectDoesntExistsException):
            await service.get_user_by_id(user_id=1)

        mock_uow.repository.retrieve.assert_awaited_once_with(1)


class TestRegisterUser:
    """Тесты для метода register_user"""

    async def test_success(self, mock_uow, expected_user, create_user_dto):
        mock_uow.repository.get_by_email.return_value = None
        mock_uow.repository.create.return_value = expected_user
        service = UserService(uow=mock_uow)

        result = await service.register_user(create_user_dto)

        assert result == expected_user
        mock_uow.repository.get_by_email.assert_awaited_once_with(create_user_dto.email)
        mock_uow.repository.create.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()

    async def test_duplicate_email_raises_error(self, mock_uow, expected_user, create_user_dto):
        mock_uow.repository.get_by_email.return_value = expected_user
        service = UserService(uow=mock_uow)

        with pytest.raises(ObjectExistsException):
            await service.register_user(create_user_dto)

        mock_uow.repository.create.assert_not_awaited()
        mock_uow.commit.assert_not_awaited()

    async def test_password_is_hashed_before_saving(self, mock_uow, expected_user, create_user_dto):
        mock_uow.repository.get_by_email.return_value = None
        mock_uow.repository.create.return_value = expected_user

        service = UserService(uow=mock_uow)
        service._hash_password = MagicMock(return_value="FAKE_HASH")
        original_password = create_user_dto.password

        await service.register_user(create_user_dto)

        service._hash_password.assert_called_once_with(original_password)
        saved_dto = mock_uow.repository.create.call_args[0][0]
        assert saved_dto.password == "FAKE_HASH"


class TestGetAllUsers:
    """Тесты для метода get_all_users"""

    async def test_can_get_all_users(self, mock_uow, expected_user):
        second_user = expected_user.model_copy(update={"id": 2, "email": "second@test.com"})

        mock_uow.repository.list.return_value = [expected_user, second_user]
        service = UserService(uow=mock_uow)

        result = await service.get_all_users()

        assert result == [expected_user, second_user]
        mock_uow.repository.list.assert_awaited_once()

    async def test_empty_list(self, mock_uow):
        mock_uow.repository.list.return_value = []
        service = UserService(uow=mock_uow)

        result = await service.get_all_users()

        assert result == []
        mock_uow.repository.list.assert_awaited_once()


class TestPasswordHashing:
    """Тесты для криптографических методов сервиса"""

    def test_hash_password_returns_different_string(self, auth_service):
        plain_password = "password"

        hashed = auth_service._hash_password(plain_password)

        assert hashed != plain_password
        assert isinstance(hashed, str)

    def test_hash_password_salts_correctly(self, auth_service):
        plain_password = "password"

        hash1 = auth_service._hash_password(plain_password)
        hash2 = auth_service._hash_password(plain_password)

        assert hash1 != hash2

    def test_verify_password_success(self, auth_service):
        plain_password = "password"
        hashed = auth_service._hash_password(plain_password)

        result = auth_service.verify_password(plain_password, hashed)
        assert result is True

    def test_verify_password_fail(self, auth_service):
        plain_password = "password"
        wrong_password = "wrong_password"
        hashed = auth_service._hash_password(plain_password)

        result = auth_service.verify_password(wrong_password, hashed)
        assert result is False
