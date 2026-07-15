import os
import pathlib
import sys
import pytest

from config.pg_config import PostgresConfig
from tools.di_containers.service_container import Container
from dependency_injector import providers
from storage.sqlalchemy.connection_proxy import AlchemyTestAsyncConnectionProxy

# Override cookiecutter placeholders so pydantic-settings can parse them.
# These env vars must be set BEFORE any config module is imported.
os.environ.setdefault("PROJECT_HOST", "127.0.0.1")
os.environ.setdefault("PROJECT_PORT", "8080")

# Ensure src/ is on the Python path when pytest is invoked from src/
src_path = str(pathlib.Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)


@pytest.fixture
def container_preparation():
    container = Container()

    test_pg_config = PostgresConfig(db_name="test_labor_exchange")
    test_dsn_string = str(test_pg_config.postgres_async_dsn)

    container.config.db.dsn.from_value(test_dsn_string)

    container.db_proxy.override(
        providers.Singleton(
            AlchemyTestAsyncConnectionProxy,
            engine_factory=container.db_engine_factory
        )
    )

    container.wire(modules=["web.api.user_router", "web.api.job_router", "web.api.response_router"])
    yield container
    container.unwire()
