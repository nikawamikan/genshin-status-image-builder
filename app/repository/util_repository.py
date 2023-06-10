from model.util_model import Artifact, JpCharacterModel, NameCard,  Weapon, Position
from lib.async_json import load_json
from pydantic import BaseModel
import asyncio

ARTIFACT_DATA_DICT: dict[str, Artifact]
CHARACTER_DATA_DICT: dict[str, JpCharacterModel]
NAMECARD_DATA_DICT: dict[str, NameCard]
WEAPON_DATA_DICT: dict[str, Weapon]
STATUS_NAMEHASH_DICT: dict[str, str]
NAMEHASH_DICT: dict[str, str]


async def base(file_name: str, model: BaseModel) -> dict[str, BaseModel]:
    data = await load_json(f"data/{file_name}")
    return {k: model(**v) for k, v in data.items()}


async def get_position_model_dict() -> dict[str, dict[str, Position]]:
    data = await load_json("data/positions.json")
    return {
        k: {k2: Position(**v2) for k2, v2 in v.items()} for k, v in data.items()
    }


async def update_artfact_model_dict():
    global ARTIFACT_DATA_DICT
    ARTIFACT_DATA_DICT = await base("artifacts.json", Artifact)


async def update_character_model_dict():
    global CHARACTER_DATA_DICT
    CHARACTER_DATA_DICT = await base("characters.json", JpCharacterModel)


async def update_namecard_model_dict():
    global NAMECARD_DATA_DICT
    NAMECARD_DATA_DICT = await base("namecards.json", NameCard)


async def update_weapon_model_dict():
    global WEAPON_DATA_DICT
    WEAPON_DATA_DICT = await base("weapons.json", Weapon)


async def update_status_namehash_model_dict():
    global STATUS_NAMEHASH_DICT
    STATUS_NAMEHASH_DICT = await load_json(f"data/statusnames.json")


async def update_namehash_model_dict():
    global NAMEHASH_DICT
    names = await load_json(f"data/names.json")
    await update_status_namehash_model_dict()
    names.update(STATUS_NAMEHASH_DICT)
    NAMEHASH_DICT = names


async def static_init():
    await update_artfact_model_dict()
    await update_character_model_dict()
    await update_namecard_model_dict()
    await update_weapon_model_dict()
    await update_status_namehash_model_dict()
    await update_namehash_model_dict()

asyncio.run(static_init())
