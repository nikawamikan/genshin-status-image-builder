from pydantic import BaseModel
from decimal import Decimal


PLAYER_IDS = set(["10000007", "10000005"])


class ShowAvatarInfo(BaseModel):
    avatarId: str
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


class ReliquarySubstat(BaseModel):
    appendPropId: str
    statValue: Decimal


class WeaponStats(BaseModel):
    appendPropId: str
    statValue: Decimal


class Flat(BaseModel):
    rankLevel: int
    equipType: str = None
    icon: str
    reliquaryMainstat: ReliquaryStat = None
    reliquarySubstats: list[ReliquarySubstat] = None
    weaponStats: list[WeaponStats] = None


class Weapon(BaseModel):
    level: int


class Equip(BaseModel):
    itemId: int
    reliquary: Reliquary = None
    weapon: Weapon = None
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
    worldLevel: int = None
    nameCardId: str
    finishAchievementNum: int = None
    towerFloorIndex: int = 0
    towerLevelIndex: int = 0
    showAvatarInfoList: list[ShowAvatarInfo] = []
    showNameCardIdList: list[int] = []
    profilePicture: ProfilePicture = None


class Enka(BaseModel):
    playerInfo: PlayerInfo
    avatarInfoList: list[AvatarInfo] = []
    uid: int
