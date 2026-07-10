from typing import Optional
from decimal import Decimal
from datetime import datetime

from bases.base_dto import BaseDTO
from pydantic import model_validator


class JobCreate(BaseDTO):
    title: str
    description: str
    salary_from: Optional[Decimal] = None
    salary_to: Optional[Decimal] = None

    @model_validator(mode='after')
    def check_salary_range(self) -> 'JobCreate':
        if self.salary_from is not None and self.salary_to is not None:
            if self.salary_from > self.salary_to:
                raise ValueError('Поле salary_from не может быть больше salary_to')
        return self


class JobUpdate(BaseDTO):
    title: Optional[str] = None
    description: Optional[str] = None
    salary_from: Optional[Decimal] = None
    salary_to: Optional[Decimal] = None
    is_active: Optional[bool] = None


class JobResponse(BaseDTO):
    id: int
    user_id: int
    title: str
    description: str
    salary_from: Optional[Decimal] = None
    salary_to: Optional[Decimal] = None
    is_active: bool
    created_at: datetime
