from unittest.mock import AsyncMock
import pytest
import datetime
from decimal import Decimal

from services.job_service import JobService
from services.exceptions import ObjectDoesntExistsException, NoPermissionException
from models.dto.job_dto import JobResponse, JobCreate, JobUpdate
from models.dto.user_dto import UserResponse


@pytest.fixture
def expected_job():
    return JobResponse(
        id=1,
        user_id=1,
        title="title",
        description="description",
        salary_from=Decimal(100),
        salary_to=Decimal(1000),
        is_active=True,
        created_at=datetime.datetime.today()
    )


@pytest.fixture
def create_job_dto():
    return JobCreate(
        title="title",
        description="description",
        salary_from=Decimal(100),
        salary_to=Decimal(1000),
    )


@pytest.fixture
def update_job_dto():
    return JobUpdate(
        title="another title",
        is_active=False
    )


@pytest.fixture
def job_list(expected_job):
    second_job = expected_job.model_copy(update={"id": 2, "title": "another title"})
    return [expected_job, second_job]


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


class TestCreateJob:
    """Тесты для метода create_job"""

    async def test_create_job_success(self, mock_uow, expected_job, create_job_dto, user_company):
        mock_uow.repository.create.return_value = expected_job
        user_service = AsyncMock()
        user_service.get_user_by_id.return_value = user_company

        job_service = JobService(uow=mock_uow, user_service=user_service)
        result = await job_service.create_job(1, create_job_dto)

        assert result == expected_job
        mock_uow.repository.create.assert_awaited_once_with(create_job_dto, 1)
        user_service.get_user_by_id.assert_awaited_once_with(1)
        mock_uow.commit.assert_awaited_once()

    async def test_create_job_fails_if_user_no_company(self, mock_uow, expected_job, create_job_dto, user_no_company):
        mock_uow.repository.create.return_value = expected_job
        user_service = AsyncMock()
        user_service.get_user_by_id.return_value = user_no_company

        job_service = JobService(uow=mock_uow, user_service=user_service)
        with pytest.raises(NoPermissionException):
            await job_service.create_job(1, create_job_dto)

        mock_uow.repository.create.assert_not_awaited()
        user_service.get_user_by_id.assert_awaited_once_with(1)
        mock_uow.commit.assert_not_awaited()


class TestGetActiveJobs:
    """Тесты для метода get_active_jobs"""

    async def test_can_get_active_jobs(self, mock_uow, job_list):
        mock_uow.repository.get_active_jobs.return_value = job_list
        service = JobService(mock_uow, None)

        result = await service.get_active_jobs()

        assert result == job_list
        mock_uow.repository.get_active_jobs.assert_awaited_once()

    async def test_empty_list(self, mock_uow):
        mock_uow.repository.get_active_jobs.return_value = []
        service = JobService(mock_uow, None)

        result = await service.get_active_jobs()

        assert result == []
        mock_uow.repository.get_active_jobs.assert_awaited_once()


class TestGetActiveUserJobs:
    """Тесты для метода get_active_user_jobs"""

    async def test_can_get_active_user_jobs(self, mock_uow, job_list):
        mock_uow.repository.get_active_jobs_by_user_id.return_value = job_list
        service = JobService(mock_uow, None)

        result = await service.get_active_user_jobs(1)

        assert result == job_list
        mock_uow.repository.get_active_jobs_by_user_id.assert_awaited_once()

    async def test_empty_list(self, mock_uow):
        mock_uow.repository.get_active_jobs_by_user_id.return_value = []
        service = JobService(mock_uow, None)

        result = await service.get_active_user_jobs(1)

        assert result == []
        mock_uow.repository.get_active_jobs_by_user_id.assert_awaited_once()


class TestGetAllJobs:
    """Тесты для метода get_all_jobs"""

    async def test_can_get_all_jobs(self, mock_uow, job_list):
        mock_uow.repository.list.return_value = job_list
        service = JobService(mock_uow, None)

        result = await service.get_all_jobs()

        assert result == job_list
        mock_uow.repository.list.assert_awaited_once()

    async def test_empty_list(self, mock_uow):
        mock_uow.repository.list.return_value = []
        service = JobService(mock_uow, None)

        result = await service.get_all_jobs()

        assert result == []
        mock_uow.repository.list.assert_awaited_once()


class TestGetAllUserJobs:
    """Тесты для метода get_all_user_jobs"""

    async def test_can_get_all_user_jobs(self, mock_uow, job_list):
        mock_uow.repository.get_jobs_by_user_id.return_value = job_list
        service = JobService(mock_uow, None)

        result = await service.get_all_user_jobs(1)

        assert result == job_list
        mock_uow.repository.get_jobs_by_user_id.assert_awaited_once()

    async def test_empty_list(self, mock_uow):
        mock_uow.repository.get_jobs_by_user_id.return_value = []
        service = JobService(mock_uow, None)

        result = await service.get_all_user_jobs(1)

        assert result == []
        mock_uow.repository.get_jobs_by_user_id.assert_awaited_once()


class TestGetJobById:
    """Тесты для метода get job by id"""
    async def test_can_get_job_by_id(self, mock_uow, expected_job):
        mock_uow.repository.retrieve.return_value = expected_job
        service = JobService(mock_uow, None)

        result = await service.get_job_by_id(1)

        assert result == expected_job
        mock_uow.repository.retrieve.assert_awaited_once_with(1)

    async def test_not_found(self, mock_uow):
        mock_uow.repository.retrieve.return_value = None
        service = JobService(mock_uow, None)

        with pytest.raises(ObjectDoesntExistsException):
            await service.get_job_by_id(1)

        mock_uow.repository.retrieve.assert_awaited_once_with(1)


class TestUpdateJob:
    """Тесты для метода update"""
    async def test_can_update_job(self, mock_uow, update_job_dto, job_list):
        mock_uow.repository.retrieve.return_value = job_list[0]
        mock_uow.repository.update.return_value = job_list[1]
        service = JobService(mock_uow, None)

        result = await service.update_job(1, 1, update_job_dto)

        assert result == job_list[1]
        mock_uow.repository.retrieve.assert_awaited_once()
        mock_uow.repository.update.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()

    async def test_cant_update_non_existent_job(self, mock_uow, update_job_dto, job_list):
        mock_uow.repository.retrieve.return_value = None
        mock_uow.repository.update.return_value = job_list[1]
        service = JobService(mock_uow, None)

        with pytest.raises(ObjectDoesntExistsException):
            await service.update_job(1, 1, update_job_dto)
        mock_uow.repository.retrieve.assert_awaited_once()
        mock_uow.repository.update.assert_not_awaited()
        mock_uow.commit.assert_not_awaited()

    async def test_cant_update_with_no_permission(self, mock_uow, update_job_dto, job_list):
        mock_uow.repository.retrieve.return_value = job_list[0]
        mock_uow.repository.update.return_value = job_list[1]
        service = JobService(mock_uow, None)

        with pytest.raises(NoPermissionException):
            await service.update_job(1, job_list[0].user_id+1, update_job_dto)
        mock_uow.repository.retrieve.assert_awaited_once()
        mock_uow.repository.update.assert_not_awaited()
        mock_uow.commit.assert_not_awaited()


class TestDeleteJob:
    """Тесты для метода delete"""
    async def test_can_delete_job(self, mock_uow, expected_job):
        mock_uow.repository.retrieve.return_value = expected_job
        service = JobService(mock_uow, None)

        await service.delete_job(1, 1)
        mock_uow.repository.retrieve.assert_awaited_once()
        mock_uow.repository.delete.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()

    async def test_cant_delete_non_existent_job(self, mock_uow):
        mock_uow.repository.retrieve.return_value = None
        service = JobService(mock_uow, None)

        with pytest.raises(ObjectDoesntExistsException):
            await service.delete_job(1, 1)
        mock_uow.repository.retrieve.assert_awaited_once()
        mock_uow.repository.delete.assert_not_awaited()
        mock_uow.commit.assert_not_awaited()

    async def test_cant_delete_with_no_permission(self, mock_uow, expected_job):
        mock_uow.repository.retrieve.return_value = expected_job
        service = JobService(mock_uow, None)

        with pytest.raises(NoPermissionException):
            await service.delete_job(1, expected_job.user_id+1)
        mock_uow.repository.retrieve.assert_awaited_once()
        mock_uow.repository.delete.assert_not_awaited()
        mock_uow.commit.assert_not_awaited()
