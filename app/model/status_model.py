from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
import service.score_calc as score_calc
import model.util_model as util_model
from repository.util_repository import \
    CHARACTER_DATA_DICT, WEAPON_DATA_DICT, ARTIFACT_DATA_DICT, STATUS_NAMEHASH_DICT, NAMECARD_DATA_DICT


ELEMENTAL_NAME_DICT = {
    "Physics": "物理ダメージ",
    "Fire": "炎元素ダメージ",
    "Electric": "雷元素ダメージ",
    "Water": "水元素ダメージ",
    "Grass": "草元素ダメージ",
    "Wind": "風元素ダメージ",
    "Rock": "岩元素ダメージ",
    "Ice": "氷元素ダメージ",
}


def get_status_base(value: Decimal, suffix: str):
    """artifactのvelueをsuffixをつけて返却します

    Returns:
        str: suffixをつけたvalueを返します
    """
    if suffix == "":
        _value = f"{value:.0f}"
    else:
        _value = f"{value:.1f}"
    return f"{_value}{suffix}"


class ArtifactStatus(BaseModel):
    value: Decimal
    name: str
    suffix: str

    @property
    def jp_name(self):
        return STATUS_NAMEHASH_DICT[self.name]

    @property
    def value_str(self):
        return get_status_base(self.value, self.suffix)

    def get_score(self, calc: score_calc.ScoreCalc):
        return calc.calc(self.name, self.value)


class Artifact(BaseModel):
    icon_name: str
    main_name: str
    main_value: Decimal
    suffix: str
    level: int
    status: list[ArtifactStatus]
    star: int
    score: Decimal = Decimal(0.0)
    util: Optional[util_model.Artifact] = None

    def set_util(self):
        self.util = ARTIFACT_DATA_DICT[self.icon_name]

    @property
    def main_jp_name(self):
        return STATUS_NAMEHASH_DICT[self.main_name]

    @property
    def main_value_str(self):
        return get_status_base(self.main_value, self.suffix)

    def set_calc_score(self, calc: score_calc.ScoreCalc):
        """スコアを計算し、scoreにsetします

        Args:
            build_type (str): ビルドのタイプ
        """
        self.score = sum([status.get_score(calc)
                         for status in self.status])


class Weapon(BaseModel):
    icon_name: str
    main_name: str
    main_value: Decimal
    sub_name: Optional[str] = None
    sub_value: Optional[Decimal] = None
    level: int
    rank: int
    util: Optional[util_model.Weapon] = None

    @property
    def main_jp_name(self):
        return STATUS_NAMEHASH_DICT[self.main_name]

    @property
    def sub_jp_name(self):
        return STATUS_NAMEHASH_DICT[self.sub_name]

    def set_util(self):
        self.util = WEAPON_DATA_DICT[self.icon_name]


class Skill(BaseModel):
    level: int
    add_level: int
    util: Optional[util_model.Skill] = None

    def set_util(self, skill: util_model.Skill):
        self.util = skill


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
    elemental_name: Optional[str] = None
    elemental_value: Optional[str] = None
    skills: list[Skill]
    artifacts: dict[str, Artifact]
    weapon: Weapon
    uid: int
    create_date: str
    costume_id: str = "defalut"
    build_type: Optional[str] = None
    costume: Optional[util_model.Costume] = None
    util: Optional[util_model.JpCharacterModel] = None

    @property
    def constellation_list(self):
        return self.util.consts[:self.constellations]

    @property
    def build_name(self):
        return score_calc.BUILD_NAMES[self.build_type]

    @property
    def elemental_jp_name(self):
        return ELEMENTAL_NAME_DICT.get(self.elemental_name)

    def init_utils(self):
        self.util = CHARACTER_DATA_DICT[self.id]
        self.costume = self.util.costumes[self.costume_id]
        self.weapon.set_util()
        for artifact in self.artifacts.values():
            artifact.set_util()
        for skill, util_skill in zip(self.skills, self.util.skills):
            skill.set_util(util_skill)

    def init_score(self):
        calc = score_calc.ScoreCalc(self.build_type)
        for artifact in self.artifacts.values():
            artifact.set_calc_score(calc)

class ProfilePicture(BaseModel):
    id: str
    costume_id: Optional[str] = "default"

    @property
    def avatar_icon(self):
        return CHARACTER_DATA_DICT[self.id].costumes[self.costume_id].avatar_icon


class UserData(BaseModel):
    uid: int
    level: int
    signature: str
    world_level: Optional[int] = None
    name_card_id: int
    name_card: Optional[util_model.NameCard] = None
    finish_achievement_num: Optional[int] = None
    tower_floor_index: int
    tower_level_index: int
    nickname: str
    create_date: str
    char_name_map: dict[str, int]
    characters: list[Character]
    profile_picture: ProfilePicture

    def set_namecard(self):
        self.name_card = NAMECARD_DATA_DICT[str(self.name_card_id)]