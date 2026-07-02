from datetime import datetime
from pydantic import EmailStr

from bases.base_dto import BaseDTO


class UserCreate(BaseDTO):
    email: EmailStr
    username: str
    password: str
    is_company: bool = False


class UserResponse(BaseDTO):
    id: int
    email: EmailStr
    username: str
    is_company: bool
    created_at: datetime


class UserResponseWithPassword(BaseDTO):
    id: int
    email: EmailStr
    username: str
    is_company: bool
    created_at: datetime
    hashed_password: str
