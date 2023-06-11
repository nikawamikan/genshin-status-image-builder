from pydantic import BaseModel
from decimal import Decimal
import model.util_model as util_model


class ArtifactStatus(BaseModel):
    value: Decimal
    name: str
    suffix: str


class Artifact(BaseModel):
    icon_name: str
    main_name: str
    main_value: Decimal
    suffix: str
    level: int
    status: list[ArtifactStatus]
    star: int
    score: Decimal = Decimal(0.0)
    util: util_model.Artifact = None


class Weapon(BaseModel):
    icon_name: str
    main_name: str
    main_value: Decimal
    sub_name: str = None
    sub_value: Decimal = None
    level: int
    rank: int
    util: util_model.Weapon = None


class Skill(BaseModel):
    level: int
    add_level: int
    util: util_model.Skill = None


class Character(BaseModel):
    id: str
    star: int
    constellations: int
    level: int
    love: int
    base_hp: int
    added_hp: int
    base_attack: int
    added_attack: int
    base_defense: int
    added_defense: int
    critical_rate: Decimal
    critical_damage: Decimal
    charge_efficiency: Decimal
    elemental_mastery: int
    elemental_name: str = None
    elemental_value: str = None
    skills: list[Skill]
    artifacts: dict[str, Artifact]
    weapon: Weapon
    uid: int
    create_date: str
    costume_id: str = "defalut"
    build_type: str = None
    costume: util_model.Costume = None
    util: util_model.JpCharacterModel = None


class UserData(BaseModel):
    uid: int
    level: int
    signature: str
    world_level: int = None
    name_card_id: int
    finish_achievement_num: int = None
    tower_floor_index: int
    tower_level_index: int
    nickname: str
    create_date: str
    char_name_map: dict[str, int]
    characters: list[Character]
