from pydantic import BaseModel
from decimal import Decimal


class ShowAvatarInfo(BaseModel):
    avatarId: int
    level: int


class ProfilePicture(BaseModel):
    avatarId: int


class Prop(BaseModel):
    type: int
    ival: str
    val: str = None


class Reliquary(BaseModel):
    level: int
    mainPropId: int
    appendPropIdList: list[int]


class ReliquaryStat(BaseModel):
    mainPropId: str
    statValue: Decimal


class WeaponStats(BaseModel):
    appendPropId: str
    statValue: Decimal


class Flat(BaseModel):
    rankLevel: int
    itemType: str
    icon: str
    reliquaryMainstat: ReliquaryStat = None
    reliquarySubstats: list[ReliquaryStat] = None
    weaponStats: list


class Weapon(BaseModel):
    level: int
    promoteLevel: int
    affixMap: dict[str, int]


class Equip(BaseModel):
    itemId: int
    reliquary: Reliquary = None
    weapon: Weapon = None


class FetterInfo(BaseModel):
    expLevel: int


class AvatarInfo(BaseModel):
    avatarId: int
    propMap: dict[str, Prop]
    talentIdList: list[int] = []
    fightPropMap: dict[str, Decimal]
    skillDepotId: int
    inherentProudSkillList: list[int]
    skillLevelMap: dict[str, int]
    proudSkillExtraLevelMap: dict[str, int] = {}
    equipList: list
    fetterInfo: FetterInfo
    costumeId: int = None


class PlayerInfo(BaseModel):
    nickname: str
    level: int
    signature: str = None
    worldLevel: int
    nameCardId: str
    finishAchievementNum: int
    towerFloorIndex: int = None
    towerLevelIndex: int = None
    showAvatarInfoList: list[ShowAvatarInfo] = []
    showNameCardIdList: list[int] = []
    profilePicture: ProfilePicture = None


class Enka(BaseModel):
    playerInfo: PlayerInfo
    avatarInfoList: list[AvatarInfo] = []
    uid: int
