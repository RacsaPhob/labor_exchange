from bases import base_dto
from pydantic import Field


class HTTPRequestDTO(base_dto.BaseDTO):
    """
    DTO, содержащий информацию для HTTP-запроса
    """

    url: str = Field(description="URL запроса")
    headers: dict | None = Field(description="Заголовки", default=None)
    query_params: dict | None = Field(description="Параметры запроса", default=None)
    payload: dict | list | None = Field(description="Body запроса", default=None)
    form_data: dict | None = Field(description="Данные из html-формы", default=None)
    files: dict | list | None = Field(description="Файлы для загрузки на сервер", default=None)


class HTTPResponseDTO(base_dto.BaseDTO):
    """
    DTO, содержащий информацию ответа HTTP-запроса
    """

    status: int = Field(description="Статус ответа")
    headers: dict | None = Field(description="Заголовки", default=None)
    payload: dict | list[dict | str | list] | str | None = Field(
        description="Body ответа", default=None
    )
