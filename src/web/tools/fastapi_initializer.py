import fastapi
from config import app_config as app_config_module
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from services import exceptions
from web.middlewares import logger_middleware
from web.tools import router_registrator

_config = app_config_module.app_config

app = fastapi.FastAPI(
    title=_config.project_name,
    version=_config.app_version,
    debug=True if _config.okd_stage == "DEV" else False,
    default_response_class=fastapi.responses.JSONResponse,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    redirect_slashes=True,
)
router_registrator.register_routers(app)

app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=["*"],  # FIXME: Только для DEV
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(logger_middleware.LogRequestInfoMiddleware)
app.add_middleware(logger_middleware.SetRequestContextMiddleware)


@app.exception_handler(exceptions.ObjectExistsException)
async def object_exists_exception_handler(
    request: Request, exc: Exception
) -> PlainTextResponse:  # noqa
    """
    Обработать ObjectExistsException
    :param request: объект запроса
    :param exc: исключение
    :return: 400 статус
    """

    return PlainTextResponse(content=str(exc), status_code=400)


@app.exception_handler(exceptions.ObjectDoesntExistsException)
async def object_doesnt_exists_exception_handler(
    request: Request, exc: Exception
) -> PlainTextResponse:  # noqa
    """
    Обработать ObjectDoesntExistsException
    :param request: объект запроса
    :param exc: исключение
    :return: 404 статус
    """

    return PlainTextResponse(content=str(exc), status_code=404)


@app.exception_handler(exceptions.NoPermissionException)
async def no_permission_exception_handler(
    request: Request, exc: Exception
) -> PlainTextResponse:  # noqa
    """
    Обработать NoPermissionException
    :param request: объект запроса
    :param exc: исключение
    :return: 403 статус
    """

    return PlainTextResponse(content=str(exc), status_code=403)


@app.exception_handler(exceptions.SystemLogicError)
async def logic_exception_handler(request: Request, exc: Exception) -> PlainTextResponse:  # noqa
    """
    Обработать SystemLogicError
    :param request: объект запроса
    :param exc: исключение
    :return: 400 статус
    """

    return PlainTextResponse(content=str(exc), status_code=400)
