import pytest
from unittest.mock import AsyncMock


@pytest.fixture
def mock_uow():
    uow = AsyncMock()

    uow.__aenter__.return_value = uow

    return uow
