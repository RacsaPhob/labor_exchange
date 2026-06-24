import json

import pytest
from fastapi.testclient import TestClient
from starlette.responses import Response
from starlette.testclient import TestClient as StarletteTestClient

from web.middlewares.logger_middleware import _bytes_to_json


class TestBytesToJson:
    def test_valid_json_object(self):
        data = {"key": "value", "num": 42}
        raw = json.dumps(data).encode()
        result = _bytes_to_json(raw)
        assert result == data

    def test_valid_json_list(self):
        data = [1, 2, 3]
        raw = json.dumps(data).encode()
        result = _bytes_to_json(raw)
        assert result == data

    def test_valid_json_string(self):
        raw = json.dumps("hello").encode()
        result = _bytes_to_json(raw)
        assert result == "hello"

    def test_valid_json_number(self):
        raw = json.dumps(42).encode()
        result = _bytes_to_json(raw)
        assert result == 42

    def test_valid_json_boolean(self):
        raw = json.dumps(True).encode()
        result = _bytes_to_json(raw)
        assert result is True

    def test_plain_text_returns_string(self):
        raw = b"not json content"
        result = _bytes_to_json(raw)
        assert isinstance(result, str)
        assert result == "not json content"

    def test_empty_bytes_returns_string(self):
        result = _bytes_to_json(b"")
        assert isinstance(result, str)
        assert result == ""

    def test_binary_data_returns_bytes(self):
        # Non-decodable bytes (invalid utf-8) → stays as bytes
        raw = bytes([0xFF, 0xFE, 0x00])
        result = _bytes_to_json(raw)
        assert isinstance(result, bytes)

    def test_nested_json_object(self):
        data = {"user": {"id": 1, "name": "Alice"}, "items": [1, 2, 3]}
        raw = json.dumps(data).encode()
        result = _bytes_to_json(raw)
        assert result == data

    def test_custom_encoding(self):
        data = {"text": "привет"}
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        result = _bytes_to_json(raw, encoding="utf-8")
        assert result == data

    def test_does_not_mutate_input(self):
        original = b'{"key": "value"}'
        original_copy = bytes(original)
        _bytes_to_json(original)
        assert original == original_copy


class TestSetRequestContextMiddleware:
    """Integration tests for SetRequestContextMiddleware."""

    def _make_app(self):
        import fastapi
        from web.middlewares.logger_middleware import SetRequestContextMiddleware

        app = fastapi.FastAPI()
        app.add_middleware(SetRequestContextMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"ok": True}

        return app

    def test_http_request_passes_through(self):
        app = self._make_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test")
        assert response.status_code == 200

    def test_non_http_scope_handled(self):
        # Lifespan events (websocket/lifespan) should not crash the middleware
        app = self._make_app()
        client = TestClient(app, raise_server_exceptions=False)
        # Simply verifying the app starts/stops without error
        with client:
            pass


class TestLogRequestInfoMiddleware:
    """Integration tests for LogRequestInfoMiddleware."""

    def _make_app(self):
        import fastapi
        from web.middlewares.logger_middleware import (
            LogRequestInfoMiddleware,
            SetRequestContextMiddleware,
        )

        app = fastapi.FastAPI()
        app.add_middleware(LogRequestInfoMiddleware)
        app.add_middleware(SetRequestContextMiddleware)

        @app.get("/ok")
        async def ok_endpoint():
            return {"status": "ok"}

        @app.get("/error")
        async def error_endpoint():
            return Response(content='{"detail":"bad request"}', status_code=400)

        @app.get("/server-error")
        async def server_error_endpoint():
            raise RuntimeError("boom")

        return app

    def test_successful_request_passes_through(self):
        app = self._make_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/ok")
        assert response.status_code == 200

    def test_400_error_response_passes_through(self):
        app = self._make_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/error")
        assert response.status_code == 400

    def test_500_error_propagates(self):
        app = self._make_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/server-error")
        assert response.status_code == 500
