import pytest
from decimal import Decimal
from pydantic import ValidationError

from models.dto.job_dto import JobCreate


class TestJobCreateDTO:
    """Тесты для схемы JobCreate и ее валидаторов"""

    def test_valid_salary_range(self):
        job = JobCreate(
            title="title",
            description="description",
            salary_from=Decimal("100000"),
            salary_to=Decimal("150000")
        )
        assert job.salary_from == Decimal("100000")
        assert job.salary_to == Decimal("150000")

    def test_equal_salary(self):
        job = JobCreate(
            title="title",
            description="description",
            salary_from=Decimal("120000"),
            salary_to=Decimal("120000")
        )
        assert job.salary_from == job.salary_to

    def test_only_salary_from_provided(self):
        job = JobCreate(
            title="title",
            description="description",
            salary_from=Decimal("100000"),
            salary_to=None
        )
        assert job.salary_from == Decimal("100000")
        assert job.salary_to is None

    def test_only_salary_to_provided(self):
        job = JobCreate(
            title="title",
            description="description",
            salary_from=None,
            salary_to=Decimal("150000")
        )
        assert job.salary_from is None
        assert job.salary_to == Decimal("150000")

    def test_no_salary_provided(self):
        job = JobCreate(
            title="title",
            description="description",
            salary_from=None,
            salary_to=None
        )
        assert job.salary_from is None
        assert job.salary_to is None

    def test_invalid_salary_range_raises_error(self):
        with pytest.raises(ValidationError):
            JobCreate(
                title="title",
                description="description",
                salary_from=Decimal("150000"),
                salary_to=Decimal("100000")
            )
