import jwt
from datetime import datetime, timedelta
from typing import Any, Dict
from config.app_config import app_config

SECRET_KEY = app_config.JWT_secret_key
ALGORITHM = app_config.JWT_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 дней


def create_access_token(data: Dict[str, Any]) -> str:
    """Создает JWT токен."""
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """
    Расшифровывает токен и возвращает данные, если он валиден.
    Иначе None.
    """
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_data
    except jwt.PyJWTError:
        return None
