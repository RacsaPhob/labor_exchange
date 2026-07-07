from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide

from models.dto import response_dto
from services.response_service import ResponseService

from tools.di_containers.service_container import Container
from web.api.dependencies import get_current_user_id
from typing import Optional, Iterable
from starlette import status

router = APIRouter(prefix="/response", tags=["Responses"])


@router.post("/create", response_model=response_dto.Response)
@inject
async def create(
    response_in: response_dto.ResponseCreate,
    current_user_id: int = Depends(get_current_user_id),
    service: ResponseService = Depends(Provide[Container.response_service])
):
    try:
        return await service.create_response(current_user_id, response_in)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Вы уже откликались на эту вакансию"
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Откликаться на вакансии может только соискатель"
        )


@router.get("/get_response", response_model=response_dto.Response)
@inject
async def get_response(
    response_id: int,
    service: ResponseService = Depends(Provide[Container.response_service])
):
    try:
        return await service.get_response_by_id(response_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отклик с такой id не найден"
        )


@router.get("/get_responses", response_model=Iterable[response_dto.Response])
@inject
async def get_responses(
    service: ResponseService = Depends(Provide[Container.response_service]),
    user_id: Optional[int] = None,
    job_id: Optional[int] = None
):
    if user_id and job_id:
        try:
            response = await service.get_response_by_user_id_and_job_id(user_id, job_id)
            return [response]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="отклик не найден"
            )

    elif user_id:
        return await service.get_user_responses(user_id)

    elif job_id:
        return await service.get_job_responses(job_id)

    return await service.get_all_responses()


@router.delete("/delete_response")
@inject
async def delete_response(
    response_id: int,
    service: ResponseService = Depends(Provide[Container.response_service]),
    current_user_id: int = Depends(get_current_user_id),

):
    try:
        return await service.delete_response(response_id, current_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="отклик с такой id не найден"
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не можете удалить чужой отклик"
        )


@router.patch("/update_response", response_model=response_dto.Response)
@inject
async def update_response(
        response_id: int,
        response_update: response_dto.ResponseUpdate,
        service: ResponseService = Depends(Provide[Container.response_service]),
        current_user_id: int = Depends(get_current_user_id),

):
    try:
        return await service.update_response(response_id, current_user_id, response_update)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="отклик с такой id не найден"
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не можете редактировать чужой отклик"
        )
