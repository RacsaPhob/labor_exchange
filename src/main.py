import uvicorn

from config import uvicorn_config

from config.pg_config import pg_config
from web.tools import fastapi_initializer

from tools.di_containers.service_container import Container

container = Container()

container.config.db.dsn.from_value(pg_config.postgres_async_dsn)
container.config.db.max_size.from_value(pg_config.connection_pool_size)

container.wire(modules=["web.api.user_router", "web.api.job_router", "web.api.response_router"])


app = fastapi_initializer.app

app.container = container


if __name__ == "__main__":
    uvicorn.run("main:app", **uvicorn_config.uvicorn_config)