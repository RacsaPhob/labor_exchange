from unittest.mock import AsyncMock
import pytest
import datetime

from services.response_service import ResponseService
from services.exceptions import ObjectDoesntExistsException, NoPermissionException, ObjectExistsException
from models.dto.response_dto import Response, ResponseCreate, ResponseUpdate
from models.dto.user_dto import UserResponse


@pytest.fixture
def expected_response():
    return Response(
        id=1,
        user_id=1,
        job_id=1,
        message="text"
    )


@pytest.fixture
def create_response_dto():
    return ResponseCreate(
        job_id=1 ,
        message="text"
    )


@pytest.fixture
def update_response_dto():
    return ResponseUpdate(
        message="new text"
    )


@pytest.fixture
def response_list(expected_response):
    second_response = expected_response.model_copy(update={"id": 2, "message": "new text"})
    return [expected_response, second_response]


@pytest.fixture
def user_company():
    return UserResponse(
        id=1,
        email="test@example.com",
        username="string",
        is_company=True,
        created_at=datetime.datetime.today()
    )


@pytest.fixture
def user_no_company(user_company):
    return user_company.model_copy(update={"is_company": False})


class TestCreateResponse:
    """Тесты для метода create_response"""

    async def test_can_create_response(self, mock_uow, create_response_dto, expected_response, user_no_company):
        mock_uow.repository.create.return_value = expected_response
        mock_uow.repository.check_exists.return_value = False
        user_service = AsyncMock()
        user_service.get_user_by_id.return_value = user_no_company

        response_service = ResponseService(mock_uow, user_service)
        result = await response_service.create_response(user_id=1, response_in=create_response_dto)

        assert result == expected_response
        user_service.get_user_by_id.assert_awaited_once_with(1)
        mock_uow.commit.assert_awaited_once()
        mock_uow.repository.create.assert_awaited_once()
        mock_uow.repository.check_exists.assert_awaited_once()

    async def test_company_user_cant_create_response(self, mock_uow, create_response_dto,
                                                     expected_response, user_company):
        mock_uow.repository.create.return_value = expected_response
        mock_uow.repository.check_exists.return_value = False
        user_service = AsyncMock()
        user_service.get_user_by_id.return_value = user_company

        response_service = ResponseService(mock_uow, user_service)
        with pytest.raises(NoPermissionException):
            await response_service.create_response(user_id=1, response_in=create_response_dto)
        user_service.get_user_by_id.assert_awaited_once_with(1)
        mock_uow.commit.assert_not_awaited()
        mock_uow.repository.create.assert_not_awaited()

    async def test_response_cant_created_twice(self, mock_uow, create_response_dto,
                                               expected_response, user_no_company):
        mock_uow.repository.create.return_value = expected_response
        mock_uow.repository.check_exists.return_value = True
        user_service = AsyncMock()
        user_service.get_user_by_id.return_value = user_no_company

        response_service = ResponseService(mock_uow, user_service)
        with pytest.raises(ObjectExistsException):
            await response_service.create_response(user_id=1, response_in=create_response_dto)
        user_service.get_user_by_id.assert_awaited_once_with(1)
        mock_uow.commit.assert_not_awaited()
        mock_uow.repository.create.assert_not_awaited()
        mock_uow.repository.check_exists.assert_awaited_once()


class TestGetResponseById:
    """Тесты для метода get_response_by_id"""

    async def test_can_get_job_by_id(self, mock_uow, expected_response):
        mock_uow.repository.retrieve.return_value = expected_response
        service = ResponseService(mock_uow, None)

        result = await service.get_response_by_id(1)

        assert result == expected_response
        mock_uow.repository.retrieve.assert_awaited_once_with(1)

    async def test_not_found(self, mock_uow):
        mock_uow.repository.retrieve.return_value = None
        service = ResponseService(mock_uow, None)

        with pytest.raises(ObjectDoesntExistsException):
            await service.get_response_by_id(1)

        mock_uow.repository.retrieve.assert_awaited_once_with(1)


class TestGetResponseByUserIdAndJobId:
    """Тесты для метода get_response_by_user_id_and_job_id"""

    async def test_can_get_job_by_ids(self, mock_uow, expected_response):
        mock_uow.repository.retrieve_by_user_id_and_job_id.return_value = expected_response
        service = ResponseService(mock_uow, None)

        result = await service.get_response_by_user_id_and_job_id(1, 1)

        assert result == expected_response
        mock_uow.repository.retrieve_by_user_id_and_job_id.assert_awaited_once_with(1, 1)

    async def test_not_found(self, mock_uow):
        mock_uow.repository.retrieve_by_user_id_and_job_id.return_value = None
        service = ResponseService(mock_uow, None)

        with pytest.raises(ObjectDoesntExistsException):
            await service.get_response_by_user_id_and_job_id(1, 1)

        mock_uow.repository.retrieve_by_user_id_and_job_id.assert_awaited_once_with(1, 1)


class TestGetUserResponses:
    """Тесты для метода get_user_responses"""

    async def test_can_get_user_responses(self, mock_uow, response_list):
        mock_uow.repository.get_by_user_id.return_value = response_list
        service = ResponseService(mock_uow, None)

        result = await service.get_user_responses(1)

        assert result == response_list
        mock_uow.repository.get_by_user_id.assert_awaited_once()

    async def test_empty_list(self, mock_uow):
        mock_uow.repository.get_by_user_id.return_value = []
        service = ResponseService(mock_uow, None)

        result = await service.get_user_responses(1)

        assert result == []
        mock_uow.repository.get_by_user_id.assert_awaited_once()


class TestGetJobResponses:
    """Тесты для метода get_job_responses"""

    async def test_can_get_job_responses(self, mock_uow, response_list):
        mock_uow.repository.get_by_job_id.return_value = response_list
        service = ResponseService(mock_uow, None)

        result = await service.get_job_responses(1)

        assert result == response_list
        mock_uow.repository.get_by_job_id.assert_awaited_once()

    async def test_empty_list(self, mock_uow):
        mock_uow.repository.get_by_job_id.return_value = []
        service = ResponseService(mock_uow, None)

        result = await service.get_job_responses(1)

        assert result == []
        mock_uow.repository.get_by_job_id.assert_awaited_once()


class TestGetAllResponses:
    """Тесты для метода get_all_responses"""

    async def test_can_get_all_responses(self, mock_uow, response_list):
        mock_uow.repository.list.return_value = response_list
        service = ResponseService(mock_uow, None)

        result = await service.get_all_responses()

        assert result == response_list
        mock_uow.repository.list.assert_awaited_once()

    async def test_empty_list(self, mock_uow):
        mock_uow.repository.list.return_value = []
        service = ResponseService(mock_uow, None)

        result = await service.get_all_responses()

        assert result == []
        mock_uow.repository.list.assert_awaited_once()


class TestUpdateResponse:
    """Тесты для метода update_response"""
    async def test_can_update_response(self, mock_uow, update_response_dto, response_list):
        mock_uow.repository.retrieve.return_value = response_list[0]
        mock_uow.repository.update.return_value = response_list[1]
        service = ResponseService(mock_uow, None)

        result = await service.update_response(1, 1, update_response_dto)

        assert result == response_list[1]
        mock_uow.repository.retrieve.assert_awaited_once()
        mock_uow.repository.update.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()

    async def test_cant_update_non_existent_response(self, mock_uow, update_response_dto, response_list):
        mock_uow.repository.retrieve.return_value = None
        mock_uow.repository.update.return_value = response_list[1]
        service = ResponseService(mock_uow, None)

        with pytest.raises(ObjectDoesntExistsException):
            await service.update_response(1, 1, update_response_dto)
        mock_uow.repository.retrieve.assert_awaited_once()
        mock_uow.repository.update.assert_not_awaited()
        mock_uow.commit.assert_not_awaited()

    async def test_cant_update_with_no_permission(self, mock_uow, update_response_dto, response_list):
        mock_uow.repository.retrieve.return_value = response_list[0]
        mock_uow.repository.update.return_value = response_list[1]
        service = ResponseService(mock_uow, None)

        with pytest.raises(NoPermissionException):
            await service.update_response(1, response_list[0].user_id+1, update_response_dto)
        mock_uow.repository.retrieve.assert_awaited_once()
        mock_uow.repository.update.assert_not_awaited()
        mock_uow.commit.assert_not_awaited()


class TestDeleteResponse:
    """Тесты для метода delete_response"""
    async def test_can_delete_response(self, mock_uow, expected_response):
        mock_uow.repository.retrieve.return_value = expected_response
        service = ResponseService(mock_uow, None)

        await service.delete_response(1, 1)
        mock_uow.repository.retrieve.assert_awaited_once()
        mock_uow.repository.delete.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()

    async def test_cant_delete_non_existent_response(self, mock_uow):
        mock_uow.repository.retrieve.return_value = None
        service = ResponseService(mock_uow, None)

        with pytest.raises(ObjectDoesntExistsException):
            await service.delete_response(1, 1)
        mock_uow.repository.retrieve.assert_awaited_once()
        mock_uow.repository.delete.assert_not_awaited()
        mock_uow.commit.assert_not_awaited()

    async def test_cant_delete_with_no_permission(self, mock_uow, expected_response):
        mock_uow.repository.retrieve.return_value = expected_response
        service = ResponseService(mock_uow, None)

        with pytest.raises(NoPermissionException):
            await service.delete_response(1, expected_response.user_id+1)
        mock_uow.repository.retrieve.assert_awaited_once()
        mock_uow.repository.delete.assert_not_awaited()
        mock_uow.commit.assert_not_awaited()
