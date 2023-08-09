from pydantic import BaseModel
from typing import Union

class Status(BaseModel):
    attack: str
    element_charge: str
    critical: str
    critical_per: str
    diffence: str
    element: str
    hp: str


class Icon(BaseModel):
    status: Status
    element: dict[Union[None, str], str]


class ArtifacterMask(BaseModel):
    alhaithem: str
    artifact_mask: str
    character_mask: str

class Constellation(BaseModel):
    lock: str
    unlock: str

class ArtifacterAssets(BaseModel):
    artifact_grades: list[str]
    background: dict[str, str]
    mask: ArtifacterMask
    reality: list[str]
    love: str
    shadow: str
    talent_back: str
    constellations: dict[str, Constellation]


class GenshinStatusAssets(BaseModel):
    star: str
    background_base: str
    background_shadow: str
    background_elements: dict[str, str]
    artufact_bg: list[str]


class ProfileAssets(BaseModel):
    layer: str

class Assets(BaseModel):
    artifacter: ArtifacterAssets
    genshin_status: GenshinStatusAssets
    profile: ProfileAssets
    icon: Icon
    icon_namehash: dict[str, str]
