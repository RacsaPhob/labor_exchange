from bases.base_dto import BaseDTO


class ResponseCreate(BaseDTO):
    job_id: int
    message: str


class ResponseUpdate(BaseDTO):
    message: str


class Response(BaseDTO):
    id: int
    user_id: int
    job_id: int
    message: str
    