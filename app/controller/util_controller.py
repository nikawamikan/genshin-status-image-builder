from fastapi import APIRouter
from fastapi.responses import Response
import service.repo_to_json as repo_to_json
import service.score_calc as score_calc
import service.character_position_service as chara_position
from model.response_json_model import CharacterPosition


router = APIRouter(prefix="/util", tags=["util"])


@router.put("/update-image")
async def get_status():
    result = await repo_to_json.updates()
    if result:
        return Response(content={"message": "image update!"}, status_code=201)
    else:
        return Response(status_code=204)


@router.get("/buildtypelist")
async def get_build_type_list():
    return score_calc.BUILD_NAMES


@router.get("/position-list")
async def get_position_data():
    return await chara_position.get_character_positions()


@router.put("/updat-eposition")
async def update_position(position: CharacterPosition):
    await chara_position.update_position_data(
        english_name=position.english_name,
        costume_id=position.id,
        position=position.position
    )
    return Response(content="position update!", status_code=201)
