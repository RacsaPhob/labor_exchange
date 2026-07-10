from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide

from models.dto import job_dto
from services.job_service import JobService

from tools.di_containers.service_container import Container
from web.api.dependencies import get_current_user_id
from typing import Optional, Iterable
from starlette import status

router = APIRouter(prefix="/job", tags=["Jobs"])


@router.post("/create", response_model=job_dto.JobResponse)
@inject
async def create(
    job_in: job_dto.JobCreate,
    current_user_id: int = Depends(get_current_user_id),
    service: JobService = Depends(Provide[Container.job_service])
):
    try:
        return await service.create_job(current_user_id, job_in)
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Соискатель не может создать вакансию"
        )


@router.get("/get_job", response_model=job_dto.JobResponse)
@inject
async def get_job(
    job_id: int,
    service: JobService = Depends(Provide[Container.job_service])
):
    try:
        return await service.get_job_by_id(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="вакансия с такой id не найдена"
        )


@router.get("/get_jobs", response_model=Iterable[job_dto.JobResponse])
@inject
async def get_jobs(
    service: JobService = Depends(Provide[Container.job_service]),
    user_id: Optional[int] = None,
    active: Optional[bool] = False
):
    if user_id and active:
        return await service.get_active_user_jobs(user_id)

    elif user_id:
        return await service.get_all_user_jobs(user_id)

    elif active:
        return await service.get_active_jobs()

    return await service.get_all_jobs()


@router.delete("/delete_job")
@inject
async def delete_job(
    job_id: int,
    service: JobService = Depends(Provide[Container.job_service]),
    current_user_id: int = Depends(get_current_user_id),

):
    try:
        return await service.delete_job(job_id, current_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="вакансия с такой id не найдена"
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не можете удалить чужую вакансию"
        )


@router.patch("/update_job", response_model=job_dto.JobResponse)
@inject
async def update_job(
        job_id: int,
        job_update: job_dto.JobUpdate,
        service: JobService = Depends(Provide[Container.job_service]),
        current_user_id: int = Depends(get_current_user_id),

):
    try:
        return await service.update_job(job_id, current_user_id, job_update)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="вакансия с такой id не найдена"
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не можете редактировать чужую вакансию"
        )
