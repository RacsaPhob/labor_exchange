import jwt
from datetime import datetime, timedelta
from freezegun import freeze_time

from tools.security.jwt_tools import create_access_token, decode_access_token
from config.app_config import app_config


class TestJWTUtils:
    """Тесты для утилит создания и проверки JWT токенов"""

    @freeze_time("2026-01-01 12:00:00")
    def test_create_access_token_contains_data_and_expiration(self):
        data = {"sub": "user", "email": "test@example.com"}
        token = create_access_token(data)

        assert isinstance(token, str)

        decoded = jwt.decode(
            token,
            app_config.JWT_secret_key,
            algorithms=[app_config.JWT_algorithm]
        )

        assert decoded["sub"] == "user"
        assert decoded["email"] == "test@example.com"

        expected_expire_date = datetime(2026, 1, 1, 12, 0, 0) + timedelta(minutes=60 * 24 * 7)
        assert decoded["exp"] == int(expected_expire_date.timestamp())

    def test_decode_valid_access_token(self):
        data = {"sub": "user"}
        token = create_access_token(data)

        decoded = decode_access_token(token)

        assert decoded is not None
        assert decoded["sub"] == "user"
        assert "exp" in decoded

    def test_decode_invalid_signature_returns_none(self):
        fake_token = jwt.encode(
            {"sub": "user"},
            "wrong_secret_key",
            algorithm=app_config.JWT_algorithm
        )

        decoded = decode_access_token(fake_token)
        assert decoded is None

    def test_decode_garbage_string_returns_none(self):
        decoded = decode_access_token("string")

        assert decoded is None

    def test_decode_expired_token_returns_none(self):
        with freeze_time("2020-01-01 12:00:00"):
            expired_token = create_access_token({"sub": "user"})

        decoded = decode_access_token(expired_token)

        assert decoded is None
