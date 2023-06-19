from fastapi import APIRouter
from fastapi.responses import FileResponse
import service.gen_genshin_image as gen_genshin_image
import model.status_model as status_model


router = APIRouter(prefix="/buildimage", tags=["image generator"])


@router.post("/genshinstat")
def get_genshin_status_build_image(char_stat: status_model.Character):
    filename = f"{char_stat.create_date}_{char_stat.uid}_{char_stat.id}_{char_stat.build_type}.jpg"
    file_path = f"build_images/{filename}"
    gen_genshin_image.save_image(
        file_path=file_path,
        character_status=char_stat,
    )
    return FileResponse(file_path, filename=filename)
