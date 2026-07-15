from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """
    Класс настроек для приложения
    """

    project_name: str = Field(
        description="Название проекта", default="api"
    )
    app_name: str = Field(
        description="Название сервиса", default="api"
    )
    app_version: str = Field(
        description="Версия API", default="v1"
    )

    app_host: str = Field(
        description="Хост сервиса",
        default="0.0.0.0",
        alias="PROJECT_HOST",
    )
    app_port: int = Field(
        description="Порт сервиса",
        default="8080",  # type: ignore[assignment]
        alias="PROJECT_PORT",
    )

    okd_stage: str = Field(
        description="Состояние OKD", default="DEV"
    )

    JWT_secret_key: str = Field(
        description="secret key для генерации jwt токенов",
        default="some-secret-key67"
    )

    JWT_algorithm: str = Field(
        description="алгоритм для генерации jwt токенов",
        default="HS256"
    )


app_config = Config()
