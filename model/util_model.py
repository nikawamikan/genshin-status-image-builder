from pydantic import BaseModel


class Icon(BaseModel):
    name: str
    path: str


class NameCard(BaseModel):
    icon: Icon


class Weapon(BaseModel):
    icon: Icon
    name: str


class Artifact(BaseModel):
    icon: Icon
    set_name: str = None
    equip_type: str


class Skill(BaseModel):
    icon: Icon
    id: str
    proud_id: str


class Costume(BaseModel):
    side_icon: Icon
    avatar_icon: Icon
    gacha_icon: Icon


class JpCharacterModel(BaseModel):
    element: str
    consts: list[Icon]
    skills: list[Skill]
    name: str
    english_name: str
    proud_map: dict[str, str]
    quality: int
    costumes: dict[str, Costume]
