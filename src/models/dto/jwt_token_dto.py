from bases.base_dto import BaseDTO


class TokenResponse(BaseDTO):
    access_token: str
    token_type: str
