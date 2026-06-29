from typing import Optional
from decimal import Decimal
from datetime import datetime

# Импортируем базовый DTO из твоего шаблона
from bases.base_dto import BaseDTO

class JobCreate(BaseDTO):
    title: str
    description: str
    salary_from: Optional[Decimal] = None
    salary_to: Optional[Decimal] = None


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
