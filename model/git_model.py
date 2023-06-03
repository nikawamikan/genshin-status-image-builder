from pydantic import BaseModel


class WeaponModel(BaseModel):
    id: int
    icon: str
    nameTextMapHash: str
    storyId: int = None


class ArtifactSetNameModel(BaseModel):
    affixId: str = None
    nameTextMapHash: str = None


class ArtifactModel(ArtifactSetNameModel):
    setId: str = None
    icon: str
    equipType: str


class CostumeModel(BaseModel):
    sideIconName: str = None
    icon: str = None
    art: str = None


class CharacterConfigModel(BaseModel):
    Element: str = None
    SkillOrder: list[str] = None
    Skills: dict[str, str] = None
    ProudMap: dict[str, str] = None
    NameTextMapHash: str = None
    QualityType: str = None
    SideIconName: str = None
    Consts: list[str] = []
    Costumes: dict[str, CostumeModel] = {}
