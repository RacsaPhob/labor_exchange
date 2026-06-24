from config import app_config
from fastapi import APIRouter

router = APIRouter(tags=["index"])

app_config_ = app_config.app_config


@router.get("/")
async def index() -> str:
    return f"{app_config_.project_name} - {app_config_.app_name}"


@router.get("/version")
async def get_version() -> str:
    return f"{app_config_.project_name} - {app_config_.app_version}"
