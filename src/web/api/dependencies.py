from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from tools.security.jwt_tools import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """Зависимость для проверки токена."""

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или просроченный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="В токене нет ID пользователя",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return int(user_id_str)
