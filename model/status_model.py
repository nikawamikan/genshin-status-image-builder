import re
from pydantic import BaseModel
from decimal import Decimal
import lib.score_calc as score_calc
from repository.util_data import STATUS_NAMEHASH_DICT, CHARACTER_DATA_DICT


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

    def get_name(self):
        return STATUS_NAMEHASH_DICT[self.name]

    def get_status(self):
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

    def get_main_name(self):
        return STATUS_NAMEHASH_DICT[self.main_name]

    def get_status(self):
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
    sub_name: str = None
    sub_value: Decimal = None
    level: int
    rank: int

    def get_main_name(self):
        return STATUS_NAMEHASH_DICT[self.main_name]

    def get_sub_name(self):
        return STATUS_NAMEHASH_DICT[self.sub_name]


class Skill(BaseModel):
    level: int
    add_level: int


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
    elemental_name: str = None
    elemental_value: str = None
    skills: list[Skill]
    artifacts: dict[str, Artifact]
    weapon: Weapon
    uid: int
    create_date: str
    costume: str = "defalut"
    build_type: str = None

    def get_name(self):
        return CHARACTER_DATA_DICT[self.id].name

    def get_gacha_icon_path(self):
        return CHARACTER_DATA_DICT[self.id].costumes[self.costume].gacha_icon

    def get_side_icon_path(self):
        return CHARACTER_DATA_DICT[self.id].costumes[self.costume].side_icon

    def get_avatar_icon_path(self):
        return CHARACTER_DATA_DICT[self.id].costumes[self.costume].avatar_icon

    def set_build_type(self, build_type: str):
        self.build_type = build_type
        calc = score_calc.ScoreCalc(build_type)
        for artifact in self.artifacts.values():
            artifact.set_calc_score(calc)


class UserData(BaseModel):
    uid: int
    level: int
    signature: str
    world_level: int
    name_card_id: int
    finish_achievement_num: int
    tower_floor_index: int
    tower_level_index: int
    nickname: str
    create_date: str
    char_name_map: dict[str, int]
    characters: list[Character]
