from fastapi import APIRouter
from fastapi.responses import FileResponse
import service.gen_genshin_image as gen_genshin_image
import service.gen_genshin_image_by_artifacter as gen_artifacter_image
import service.gen_profile_image as gen_profile_image
import model.status_model as status_model


router = APIRouter(prefix="/buildimage", tags=["image generator"])


@router.post("/genshinstat/{gen_type}/")
def get_genshin_status_build_image(char_stat: status_model.Character, gen_type:int = 0):
    filename = f"{char_stat.create_date}_{char_stat.uid}_{char_stat.id}_{char_stat.build_type}_{gen_type}hoge.jpg"
    file_path = f"build_images/{filename}"
    if gen_type == 0:
        gen_genshin_image.save_image(
            file_path=file_path,
            character_status=char_stat,
        )
    elif gen_type == 1:
        gen_artifacter_image.save_image(
            file_path=file_path,
            character_status=char_stat,
        )
    return FileResponse(file_path, filename=filename)

@router.post("/profile/")
def get_genshin_status_build_image(user_data: status_model.UserData):
    filename = f"{user_data.create_date}_{user_data.create_date}_{user_data.uid}.jpg"
    file_path = f"profile_images/{filename}"
    gen_profile_image.save_image(
        file_path=file_path,
        userdata=user_data,
    )
    return FileResponse(file_path, filename=filename)