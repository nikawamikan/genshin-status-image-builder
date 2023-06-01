from model.util_model import Artifact, JpCharacterModel, NameCard,  Weapon
from lib.async_json import load_json
from pydantic import BaseModel
import asyncio


async def base(file_name: str, model: BaseModel) -> dict[str, BaseModel]:
    data = await load_json(f"data/{file_name}")
    return {k: model(**v) for k, v in data.items()}


async def get_artfact_model_dict() -> dict[str, Artifact]:
    return await base("artifacts.json", Artifact)


async def get_character_model_dict() -> dict[str, JpCharacterModel]:
    return await base("characters.json", JpCharacterModel)


async def get_namecard_model_dict() -> dict[str, NameCard]:
    return await base("namecards.json", NameCard)


async def get_weapon_model_dict() -> dict[str, Weapon]:
    return await base("weapons.json", Weapon)


async def get_status_namehash_model_dict() -> dict[str, str]:
    return await load_json(f"data/statusnames.json")


async def get_namehash_model_dict() -> dict[str, str]:
    names = await load_json(f"data/names.json")
    update_names = await get_status_namehash_model_dict()
    names.update(update_names)
    return names

ARTIFACT_DATA_DICT = {}
CHARACTER_DATA_DICT = {}
NAMECARD_DATA_DICT = {}
WEAPON_DATA_DICT = {}
STATUS_NAMEHASH_DICT = {}
NAMEHASH_DICT = {}


async def static_init():
    global ARTIFACT_DATA_DICT
    global CHARACTER_DATA_DICT
    global NAMECARD_DATA_DICT
    global NAMECARD_DATA_DICT
    global WEAPON_DATA_DICT
    global STATUS_NAMEHASH_DICT
    global NAMEHASH_DICT

    ARTIFACT_DATA_DICT = await get_artfact_model_dict()
    CHARACTER_DATA_DICT = await get_character_model_dict()
    NAMECARD_DATA_DICT = await get_namecard_model_dict()
    WEAPON_DATA_DICT = await get_weapon_model_dict()
    STATUS_NAMEHASH_DICT = await get_status_namehash_model_dict()
    NAMEHASH_DICT = await get_namehash_model_dict()

asyncio.run(static_init())
