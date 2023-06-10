from lib.gen_genshin_image import save_image
from model.enka_model import get_json, Character, get_user_data
from fastapi.responses import FileResponse
from fastapi import FastAPI
from ordered_set import OrderedSet
from app.service import score_calc
import os
import glob

URL_CACHE = OrderedSet(glob.glob('build_images/*.jpeg'))
MAX_CACHE_SIZE = 1000
CALC_TYPE_MAP = {v: k for k, v in score_calc.BUILD_NAMES.items()}


def cache_append(file_path: str):
    URL_CACHE.add(file_path)
    if len(URL_CACHE) > MAX_CACHE_SIZE:
        image_path = URL_CACHE.pop(0)
        try:
            os.remove(image_path)
        except:
            pass


app = FastAPI()


@app.post("/build")
async def get_build(char_stat: Character):
    lang = "ja"
    filename = f"{char_stat.create_date}_{char_stat.uid}_{char_stat.english_name}_{char_stat.build_type}_{lang}.jpg"
    file_path = f"build_images/{filename}"
    if file_path not in URL_CACHE:
        char_stat.set_build_type(score_calc.BUILD_NAMES[char_stat.build_type])
        save_image(file_path=file_path, character_status=char_stat)
        cache_append(file_path=file_path)
    return FileResponse(file_path, filename=filename)


@app.get("/build_types.json")
async def get_build_types():
    return CALC_TYPE_MAP


@app.get("/userdata/{uid}.json")
async def get_user_json(uid: int):
    json = get_user_data(await get_json(uid))
    return json
