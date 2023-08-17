from fastapi import APIRouter, HTTPException
import service.status_service as status_service
import repository.enka_repository as enka_repository
from aiohttp import client_exceptions
from fastapi.responses import Response


router = APIRouter(prefix="/status", tags=["status data"])


@router.get("/uid/{uid}")
async def get_status(uid: int):
    try:
        return await status_service.get_user_data(uid)
    except client_exceptions.ClientResponseError as e:
        print(e)
        raise HTTPException(status_code=e.status, detail=e.message)
