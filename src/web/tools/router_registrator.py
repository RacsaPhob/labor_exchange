from fastapi import FastAPI

from config import app_config as app_config_module
from web.entrypoints import index_entrypoint

from web.api import user_router, job_router, response_router

_config = app_config_module.app_config


def register_routers(app: FastAPI) -> None:
    app.include_router(index_entrypoint.router, prefix=f"/api/{_config.app_version}")

    app.include_router(
        user_router.router, 
        prefix=f"/api/{_config.app_version}",
        tags=["Users"],
    )

    app.include_router(
        job_router.router,
        prefix=f"/api/{_config.app_version}",
        tags=["Jobs"],
    )

    app.include_router(
        response_router.router,
        prefix=f"/api/{_config.app_version}",
        tags=["Responses"],
    )
