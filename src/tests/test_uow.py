"""
Tests for Unit of Work implementations using mocked sessions.

Uses TestBaseAlchemySyncUOW / TestBaseAlchemyAsyncUOW (from base_alchemy_uow)
and TestAlchemySyncUOW / TestAlchemyAsyncUOW (from generic_alchemy_uow).
Both families mock out the database session so no real DB is needed.

These tests are skipped automatically when SQLAlchemy modules are not present
(i.e. when the project was generated without add_sql_alchemy=True).
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

pytest.importorskip("bases.uows.base_alchemy_uow", reason="SQLAlchemy not enabled (add_sql_alchemy=False)")

from bases.uows.base_alchemy_uow import (
    BaseAlchemyAsyncUOW,
    BaseAlchemySyncUOW,
    TestBaseAlchemyAsyncUOW,
    TestBaseAlchemySyncUOW,
)
from bases.uows.generic_alchemy_uow import (
    AlchemyAsyncGenericUOW,
    AlchemySyncGenericUOW,
    TestAlchemyAsyncUOW,
    TestAlchemySyncUOW,
)


# ---------------------------------------------------------------------------
# Helpers – fully mocked repository / connection_proxy
# ---------------------------------------------------------------------------

def _make_sync_repo() -> MagicMock:
    """Return a mock repository whose connection_proxy returns a mock Session."""
    session = MagicMock()
    session.begin.return_value = MagicMock()  # mock transaction

    proxy = MagicMock()
    proxy.connect.return_value = session

    repo = MagicMock()
    repo.connection_proxy = proxy
    return repo


def _make_async_repo() -> MagicMock:
    """Return a mock repository whose connection_proxy returns a mock AsyncSession."""
    session = AsyncMock()
    # in_transaction() is a sync method on AsyncSession — use MagicMock
    session.in_transaction = MagicMock(return_value=False)
    session.begin = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    proxy = AsyncMock()
    proxy.connect = AsyncMock(return_value=session)
    proxy.disconnect = AsyncMock()

    repo = MagicMock()
    repo.connection_proxy = proxy
    return repo


# ---------------------------------------------------------------------------
# BaseAlchemySyncUOW
# ---------------------------------------------------------------------------

class TestBaseAlchemySyncUOWBehavior:
    def test_commit_raises_when_no_transaction(self):
        repo = _make_sync_repo()
        uow = BaseAlchemySyncUOW(repo)
        with pytest.raises(ValueError, match="транзакции"):
            uow.commit()

    def test_rollback_raises_when_no_transaction(self):
        repo = _make_sync_repo()
        uow = BaseAlchemySyncUOW(repo)
        with pytest.raises(ValueError, match="транзакции"):
            uow.rollback()

    def test_context_manager_calls_disconnect_on_success(self):
        repo = _make_sync_repo()
        with BaseAlchemySyncUOW(repo):
            pass
        repo.connection_proxy.disconnect.assert_called_once()

    def test_context_manager_calls_rollback_on_exception(self):
        repo = _make_sync_repo()
        uow = BaseAlchemySyncUOW(repo)
        transaction = repo.connection_proxy.connect().begin()
        try:
            with uow:
                raise RuntimeError("fail")
        except RuntimeError:
            pass
        transaction.rollback.assert_called()

    def test_commit_marks_transaction_committed(self):
        repo = _make_sync_repo()
        uow = BaseAlchemySyncUOW(repo)
        with uow:
            uow.commit()
        assert uow._is_transaction_commited is True


# ---------------------------------------------------------------------------
# TestBaseAlchemySyncUOW (the test-double provided by the template)
# ---------------------------------------------------------------------------

class TestBaseAlchemySyncUOWDouble:
    def test_enter_returns_self(self):
        repo = _make_sync_repo()
        uow = TestBaseAlchemySyncUOW(repo)
        result = uow.__enter__()
        assert result is uow

    def test_commit_calls_session_commit(self):
        repo = _make_sync_repo()
        uow = TestBaseAlchemySyncUOW(repo)
        with uow:
            uow.commit()
        uow._session.commit.assert_called()

    def test_rollback_calls_session_rollback(self):
        repo = _make_sync_repo()
        uow = TestBaseAlchemySyncUOW(repo)
        with uow:
            uow.rollback()
        uow._session.rollback.assert_called()

    def test_exception_triggers_rollback(self):
        repo = _make_sync_repo()
        uow = TestBaseAlchemySyncUOW(repo)
        try:
            with uow:
                raise ValueError("oops")
        except ValueError:
            pass
        uow._session.rollback.assert_called()

    def test_success_triggers_disconnect(self):
        repo = _make_sync_repo()
        uow = TestBaseAlchemySyncUOW(repo)
        with uow:
            pass
        repo.connection_proxy.disconnect.assert_called()


# ---------------------------------------------------------------------------
# BaseAlchemyAsyncUOW
# ---------------------------------------------------------------------------

class TestBaseAlchemyAsyncUOWBehavior:
    async def test_commit_raises_when_no_transaction(self):
        repo = _make_async_repo()
        uow = BaseAlchemyAsyncUOW(repo)
        with pytest.raises(ValueError, match="транзакции"):
            await uow.commit()

    async def test_rollback_raises_when_no_transaction(self):
        repo = _make_async_repo()
        uow = BaseAlchemyAsyncUOW(repo)
        with pytest.raises(ValueError, match="транзакции"):
            await uow.rollback()

    async def test_context_manager_calls_disconnect_on_success(self):
        repo = _make_async_repo()
        async with BaseAlchemyAsyncUOW(repo):
            pass
        repo.connection_proxy.disconnect.assert_awaited_once()

    async def test_commit_marks_transaction_committed(self):
        repo = _make_async_repo()
        uow = BaseAlchemyAsyncUOW(repo)
        async with uow:
            await uow.commit()
        assert uow._is_transaction_commited is True

    async def test_context_manager_calls_rollback_on_exception(self):
        repo = _make_async_repo()
        uow = BaseAlchemyAsyncUOW(repo)
        try:
            async with uow:
                raise RuntimeError("fail")
        except RuntimeError:
            pass
        repo.connection_proxy.connect.return_value.rollback.assert_awaited()


# ---------------------------------------------------------------------------
# TestBaseAlchemyAsyncUOW (the test-double provided by the template)
# ---------------------------------------------------------------------------

class TestBaseAlchemyAsyncUOWDouble:
    async def test_enter_returns_self(self):
        repo = _make_async_repo()
        uow = TestBaseAlchemyAsyncUOW(repo)
        result = await uow.__aenter__()
        assert result is uow

    async def test_commit_calls_session_commit(self):
        repo = _make_async_repo()
        uow = TestBaseAlchemyAsyncUOW(repo)
        async with uow:
            await uow.commit()
        uow._session.commit.assert_awaited()

    async def test_rollback_calls_session_rollback(self):
        repo = _make_async_repo()
        uow = TestBaseAlchemyAsyncUOW(repo)
        async with uow:
            await uow.rollback()
        uow._session.rollback.assert_awaited()

    async def test_exception_triggers_rollback(self):
        repo = _make_async_repo()
        uow = TestBaseAlchemyAsyncUOW(repo)
        try:
            async with uow:
                raise ValueError("oops")
        except ValueError:
            pass
        uow._session.rollback.assert_awaited()

    async def test_success_triggers_disconnect(self):
        repo = _make_async_repo()
        uow = TestBaseAlchemyAsyncUOW(repo)
        async with uow:
            pass
        repo.connection_proxy.disconnect.assert_awaited()


# ---------------------------------------------------------------------------
# AlchemySyncGenericUOW / TestAlchemySyncUOW
# ---------------------------------------------------------------------------

class TestAlchemySyncGenericUOWBehavior:
    def test_commit_raises_when_no_transaction(self):
        repo = _make_sync_repo()
        uow = AlchemySyncGenericUOW(repo)
        with pytest.raises(ValueError):
            uow.commit()

    def test_rollback_raises_when_no_transaction(self):
        repo = _make_sync_repo()
        uow = AlchemySyncGenericUOW(repo)
        with pytest.raises(ValueError):
            uow.rollback()

    def test_context_manager_success_calls_disconnect(self):
        repo = _make_sync_repo()
        with AlchemySyncGenericUOW(repo):
            pass
        repo.connection_proxy.disconnect.assert_called_once()


class TestAlchemySyncGenericUOWDouble:
    def test_enter_returns_self(self):
        repo = _make_sync_repo()
        uow = TestAlchemySyncUOW(repo)
        assert uow.__enter__() is uow

    def test_commit_delegates_to_session(self):
        repo = _make_sync_repo()
        uow = TestAlchemySyncUOW(repo)
        with uow:
            uow.commit()
        uow._session.commit.assert_called()

    def test_rollback_delegates_to_session(self):
        repo = _make_sync_repo()
        uow = TestAlchemySyncUOW(repo)
        with uow:
            uow.rollback()
        uow._session.rollback.assert_called()

    def test_exception_triggers_rollback(self):
        repo = _make_sync_repo()
        uow = TestAlchemySyncUOW(repo)
        try:
            with uow:
                raise ValueError("error")
        except ValueError:
            pass
        uow._session.rollback.assert_called()


# ---------------------------------------------------------------------------
# AlchemyAsyncGenericUOW / TestAlchemyAsyncUOW
# ---------------------------------------------------------------------------

class TestAlchemyAsyncGenericUOWBehavior:
    async def test_commit_raises_when_no_transaction(self):
        repo = _make_async_repo()
        uow = AlchemyAsyncGenericUOW(repo)
        with pytest.raises(ValueError):
            await uow.commit()

    async def test_context_manager_success_calls_disconnect(self):
        repo = _make_async_repo()
        async with AlchemyAsyncGenericUOW(repo):
            pass
        repo.connection_proxy.disconnect.assert_awaited_once()


class TestAlchemyAsyncGenericUOWDouble:
    async def test_enter_returns_self(self):
        repo = _make_async_repo()
        uow = TestAlchemyAsyncUOW(repo)
        result = await uow.__aenter__()
        assert result is uow

    async def test_commit_delegates_to_session(self):
        repo = _make_async_repo()
        uow = TestAlchemyAsyncUOW(repo)
        async with uow:
            await uow.commit()
        uow._session.commit.assert_awaited()

    async def test_rollback_delegates_to_session(self):
        repo = _make_async_repo()
        uow = TestAlchemyAsyncUOW(repo)
        async with uow:
            await uow.rollback()
        uow._session.rollback.assert_awaited()

    async def test_exception_triggers_rollback(self):
        repo = _make_async_repo()
        uow = TestAlchemyAsyncUOW(repo)
        try:
            async with uow:
                raise ValueError("async error")
        except ValueError:
            pass
        uow._session.rollback.assert_awaited()

    async def test_success_triggers_disconnect(self):
        repo = _make_async_repo()
        uow = TestAlchemyAsyncUOW(repo)
        async with uow:
            pass
        repo.connection_proxy.disconnect.assert_awaited()
