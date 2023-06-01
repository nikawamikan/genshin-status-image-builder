from model.util_model import Artifact, JpCharacterModel, NameCard,  Weapon
from lib.async_json import load_json
from pydantic import BaseModel


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


async def get_namehash_model_dict() -> dict[str, str]:
    names = await load_json(f"data/names.json")
    update_names = await load_json(f"data/statusnames.json")
    names.update(update_names)
    return names
