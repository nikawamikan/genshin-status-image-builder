from fastapi import APIRouter
import service.status_service as status_service
import repository.enka_repository as enka_repository


router = APIRouter(prefix="/status", tags=["status data"])


@router.get("/uid/{uid}")
async def get_status(uid: int):
    return await status_service.get_user_data(uid)
