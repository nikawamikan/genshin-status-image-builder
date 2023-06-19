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


class ArtifacterAssets(BaseModel):
    artifact_grades: list[str]
    background: dict[str, str]
    mask: ArtifacterMask
    rarlity: list[str]
    love: str
    shadow: str
    talent_back: str


class GenshinStatusAssets(BaseModel):
    star: str
    background_base: str
    background_shadow: str
    backgroundo_elements: dict[str, str]
    artufact_bg: list[str]


class Assets(BaseModel):
    artifacter: ArtifacterAssets
    genshin_status: GenshinStatusAssets
    icon: Icon
    icon_namehash: dict[str, str]
