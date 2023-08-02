from pydantic import BaseModel
from typing import Optional


class WeaponModel(BaseModel):
    id: int
    icon: str
    nameTextMapHash: str
    storyId: Optional[int] = None


class ArtifactSetNameModel(BaseModel):
    affixId: Optional[str] = None
    nameTextMapHash: Optional[str] = None


class ArtifactModel(ArtifactSetNameModel):
    setId: Optional[str] = None
    icon: str
    equipType: str


class CostumeModel(BaseModel):
    sideIconName: Optional[str] = None
    icon: Optional[str] = None
    art: Optional[str] = None


class CharacterConfigModel(BaseModel):
    Element: Optional[str] = None
    SkillOrder: Optional[list[str]] = None
    Skills: Optional[dict[str, str]] = None
    ProudMap: Optional[dict[str, str]] = None
    NameTextMapHash: Optional[str] = None
    QualityType: Optional[str] = None
    SideIconName: Optional[str] = None
    Consts: list[str] = []
    Costumes: dict[str, CostumeModel] = {}
