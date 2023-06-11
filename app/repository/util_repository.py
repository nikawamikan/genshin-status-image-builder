from model.util_model import Artifact, JpCharacterModel,  NameCard,  Weapon, Position
from lib.json_lib import load_json
from pydantic import BaseModel
import asyncio


ARTIFACT_DATA_DICT: dict[str, Artifact]
CHARACTER_DATA_DICT: dict[str, JpCharacterModel]
NAMECARD_DATA_DICT: dict[str, NameCard]
WEAPON_DATA_DICT: dict[str, Weapon]
STATUS_NAMEHASH_DICT: dict[str, str]
NAMEHASH_DICT: dict[str, str]


def base(file_name: str, model: BaseModel) -> dict[str, BaseModel]:
    data = load_json(f"data/{file_name}")
    return {k: model(**v) for k, v in data.items()}


def get_position_model_dict() -> dict[str, dict[str, Position]]:
    data = load_json("data/positions.json")
    return {
        k: {k2: Position(**v2) for k2, v2 in v.items()} for k, v in data.items()
    }


def update_artfact_model_dict():
    global ARTIFACT_DATA_DICT
    ARTIFACT_DATA_DICT = base("artifacts.json", Artifact)


def update_character_model_dict():
    global CHARACTER_DATA_DICT
    CHARACTER_DATA_DICT = base("characters.json", JpCharacterModel)


def update_namecard_model_dict():
    global NAMECARD_DATA_DICT
    NAMECARD_DATA_DICT = base("namecards.json", NameCard)


def update_weapon_model_dict():
    global WEAPON_DATA_DICT
    WEAPON_DATA_DICT = base("weapons.json", Weapon)


def update_status_namehash_model_dict():
    global STATUS_NAMEHASH_DICT
    STATUS_NAMEHASH_DICT = load_json(f"data/statusnames.json")


def update_namehash_model_dict():
    global NAMEHASH_DICT
    names = load_json(f"data/names.json")
    update_status_namehash_model_dict()
    names.update(STATUS_NAMEHASH_DICT)
    NAMEHASH_DICT = names


def static_init():
    update_artfact_model_dict()
    update_character_model_dict()
    update_namecard_model_dict()
    update_weapon_model_dict()
    update_status_namehash_model_dict()
    update_namehash_model_dict()


static_init()
