from decimal import Decimal
import re
import datetime
import model.status_model as status_model
import model.enka_model as enka_model
import repository.enka_repository as enka_repository
from repository.util_repository import CHARACTER_DATA_DICT
import redis
import json


TTL = 600


pool = redis.ConnectionPool(host="redis")
redis_obj = redis.StrictRedis(connection_pool=pool)

PERCENT_PATTERN = re.compile(
    r"PERCENT|CRITICAL|FIGHT_PROP_CHARGE_EFFICIENCY|_ADD_HURT"
)


def get_suffix(name: str):
    if PERCENT_PATTERN.search(name):
        return "%"
    return ""


ELEMENT_MAP = {
    "Physics": "30",
    "Fire": "40",
    "Electric": "41",
    "Water": "42",
    "Grass": "43",
    "Wind": "44",
    "Rock": "45",
    "Ice": "46",
}


ELEMENT_DAMAGE_TYPES = {
    v: k for k, v in ELEMENT_MAP.items()
}


def check_traveler(id: int):
    return id in ["10000007", "10000005"]


def get_characters(
    uid: int,
    create_date: str,
    avatar_info_list: list[enka_model.AvatarInfo]
) -> list[status_model.Character]:
    characters = [
        get_character_status(uid, create_date, v) for v in avatar_info_list
    ]
    return characters


def get_artifact(equip: enka_model.Equip):
    flat = equip.flat
    icon_name = flat.icon
    main_name = flat.reliquaryMainstat.mainPropId
    main_value = flat.reliquaryMainstat.statValue
    flat.reliquarySubstats
    suffix = get_suffix(main_name)
    level = equip.reliquary.level - 1
    star = flat.rankLevel
    status = [
        status_model.ArtifactStatus(
            value=round(v.statValue, 1),
            name=v.appendPropId,
            suffix=get_suffix(v.appendPropId),
        ) for v in flat.reliquarySubstats
    ]
    return status_model.Artifact(
        icon_name=icon_name,
        main_name=main_name,
        star=star,
        main_value=main_value,
        suffix=suffix,
        level=level,
        status=status,
    )


def get_artifacts(equip_list: list[enka_model.Equip]) -> dict[str, status_model.Artifact]:
    return {
        equip.flat.equipType: get_artifact(equip)
        for equip in equip_list
    }


def get_weapon(equip: enka_model.Equip):
    flat = equip.flat
    icon_name = flat.icon
    main_name = flat.weaponStats[0].appendPropId
    main_value = flat.weaponStats[0].statValue
    sub_name = None
    sub_value = None
    if len(flat.weaponStats) == 2:
        sub_name = flat.weaponStats[1].appendPropId
        sub_value = flat.weaponStats[1].statValue
    level = equip.weapon.level
    rank = flat.rankLevel
    return status_model.Weapon(
        icon_name=icon_name,
        main_name=main_name,
        main_value=main_value,
        sub_name=sub_name,
        sub_value=sub_value,
        level=level,
        rank=rank
    )


def get_skills(id: str, skill_levels: dict[str, int], extra_skill_levels: dict[str, int]):
    return [
        status_model.Skill(
            level=skill_levels[v.id],
            add_level=extra_skill_levels[v.proud_id] if v.proud_id in extra_skill_levels else 0,
        )for v in CHARACTER_DATA_DICT[id].skills
    ]


def get_elemental_name_value(id: str, avatar_info: enka_model.AvatarInfo):

    elemental_name = None
    elemental_value = None

    max_value = Decimal(0)
    max_key = None
    for k in ELEMENT_DAMAGE_TYPES.keys():
        if max_value < avatar_info.fightPropMap[k]:
            max_value = avatar_info.fightPropMap[k]
            max_key = k
    character_element = CHARACTER_DATA_DICT[id].element
    if max_key is not None:
        if max_value == avatar_info.fightPropMap[ELEMENT_MAP[character_element]]:
            elemental_name = character_element
        else:
            elemental_name = ELEMENT_DAMAGE_TYPES[max_key]
        elemental_value = f"{round(max_value*100, 1)}%"

    return (elemental_name, elemental_value)


def get_character_status(uid: int, create_date: str, avatar_info: enka_model.AvatarInfo):
    id = avatar_info.avatarId
    if check_traveler(id):
        id = f"{id}-{avatar_info.skillDepotId}"
    star = CHARACTER_DATA_DICT[id].quality
    constellations = len(CHARACTER_DATA_DICT[id].consts)
    level = int(avatar_info.propMap["4001"].val)
    base_hp = int(avatar_info.fightPropMap["1"])
    added_hp = avatar_info.fightPropMap["2000"] - base_hp

    base_attack = int(avatar_info.fightPropMap["4"])
    added_attack = int(avatar_info.fightPropMap["2001"]) - base_attack
    base_defense = int(avatar_info.fightPropMap["7"])
    added_defense = int(avatar_info.fightPropMap["2002"]) - base_defense
    critical_rate = round(avatar_info.fightPropMap["20"] * 100, 1)
    critical_damage = round(avatar_info.fightPropMap["22"] * 100, 1)
    charge_efficiency = round(avatar_info.fightPropMap["23"] * 100, 1)
    elemental_mastery = int(avatar_info.fightPropMap["28"])
    love = avatar_info.fetterInfo.expLevel

    elemental_name, elemental_value = get_elemental_name_value(id, avatar_info)
    skills = get_skills(
        id,
        avatar_info.skillLevelMap,
        avatar_info.proudSkillExtraLevelMap
    )
    artifacts = get_artifacts(avatar_info.equipList[:-1])
    weapon = get_weapon(avatar_info.equipList[-1])
    return status_model.Character(
        id=id,
        star=star,
        constellations=constellations,
        level=level,
        love=love,
        base_hp=base_hp,
        added_hp=added_hp,
        base_attack=base_attack,
        added_attack=added_attack,
        base_defense=base_defense,
        added_defense=added_defense,
        critical_rate=critical_rate,
        critical_damage=critical_damage,
        charge_efficiency=charge_efficiency,
        elemental_mastery=elemental_mastery,
        elemental_name=elemental_name,
        elemental_value=elemental_value,
        skills=skills,
        artifacts=artifacts,
        weapon=weapon,
        uid=uid,
        create_date=create_date,
        costume_id=avatar_info.costumeId
    )


async def get_user_data(uid) -> status_model.UserData:
    if redis_obj.keys(uid):
        return status_model.UserData(** json.loads(redis_obj.get(uid)))

    enka = await enka_repository.get_enka_model(uid)
    create_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    char_name_map = {CHARACTER_DATA_DICT[c.avatarId].name: i for i, c in enumerate(
        enka.playerInfo.showAvatarInfoList)}
    char_list = get_characters(enka.uid, create_date, enka.avatarInfoList)

    user_data = status_model.UserData(
        uid=enka.uid,
        level=enka.playerInfo.level,
        signature=enka.playerInfo.signature,
        world_level=enka.playerInfo.worldLevel,
        name_card_id=enka.playerInfo.nameCardId,
        finish_achievement_num=enka.playerInfo.finishAchievementNum,
        tower_floor_index=enka.playerInfo.towerFloorIndex,
        tower_level_index=enka.playerInfo.towerLevelIndex,
        nickname=enka.playerInfo.nickname,
        create_date=create_date,
        char_name_map=char_name_map,
        characters=char_list,
    )
    redis_obj.set(uid, user_data.json())
    redis_obj.expire(uid, TTL)
    return user_data
