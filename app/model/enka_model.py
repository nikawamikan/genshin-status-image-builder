from pydantic import BaseModel
from decimal import Decimal
from typing import Optional


PLAYER_IDS = set(["10000007", "10000005"])


class ShowAvatarInfo(BaseModel):
    avatarId: str
    level: int


class ProfilePicture(BaseModel):
    avatarId: str
    costumeId: str = "default"


class Prop(BaseModel):
    type: int
    ival: str
    val: Optional[str] = None


class Reliquary(BaseModel):
    level: int
    mainPropId: int
    appendPropIdList: list[int]


class ReliquaryStat(BaseModel):
    mainPropId: str
    statValue: Decimal


class ReliquarySubstat(BaseModel):
    appendPropId: str
    statValue: Decimal


class WeaponStats(BaseModel):
    appendPropId: str
    statValue: Decimal


class Flat(BaseModel):
    rankLevel: int
    equipType: Optional[str] = None
    icon: str
    reliquaryMainstat: Optional[ReliquaryStat] = None
    reliquarySubstats: Optional[list[ReliquarySubstat]] = None
    weaponStats: Optional[list[WeaponStats]] = None


class Weapon(BaseModel):
    level: int
    affixMap: Optional[dict] = {"0":0}


class Equip(BaseModel):
    itemId: int
    reliquary: Optional[Reliquary] = None
    weapon: Optional[Weapon] = None
    flat: Flat


class FetterInfo(BaseModel):
    expLevel: int


class AvatarInfo(BaseModel):
    avatarId: str
    propMap: dict[str, Prop]
    talentIdList: list[int] = []
    fightPropMap: dict[str, Decimal]
    skillDepotId: int
    inherentProudSkillList: list[int]
    skillLevelMap: dict[str, int]
    proudSkillExtraLevelMap: dict[str, int] = {}
    equipList: list[Equip]
    fetterInfo: FetterInfo
    costumeId: str = "default"

    def get_avatar_id(self):
        if self.avatarId in PLAYER_IDS:
            return f"{self.avatarId}-{self.skillDepotId}"
        else:
            return self.avatarId


class PlayerInfo(BaseModel):
    nickname: str
    level: int
    signature: str = ""
    worldLevel: Optional[int] = None
    nameCardId: str
    finishAchievementNum: Optional[int] = None
    towerFloorIndex: int = 0
    towerLevelIndex: int = 0
    showAvatarInfoList: list[ShowAvatarInfo] = []
    showNameCardIdList: list[int] = []
    profilePicture: ProfilePicture = ProfilePicture(
        avatarId="10000007",
        costumeId="default",
    )


class Enka(BaseModel):
    playerInfo: PlayerInfo
    avatarInfoList: list[AvatarInfo] = []
    uid: int
