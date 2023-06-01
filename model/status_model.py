import re
from pydantic import BaseModel
from decimal import Decimal
import lib.score_calc as score_calc

PERCENT_PATTERN = re.compile(r"%|会心|チャ|元素ダメ")


def get_suffix(name: str):
    if PERCENT_PATTERN.search(name):
        return "%"
    return ""


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

    def get_status(self):
        return get_status_base(self.value, self.suffix)

    def get_score(self, build_type: str):
        return score_calc.calc(self.name, self.value, build_type)


class Artifact(BaseModel):
    icon: str
    main_name: str
    main_value: str
    suffix: str
    level: int
    status: list[ArtifactStatus]
    artifact_set_name: str
    star: int
    score: Decimal = 0.0

    def get_status(self):
        return get_status_base(self.main_value, self.suffix)

    def set_calc_score(self, build_type: str):
        """スコアを計算し、scoreにsetします

        Args:
            build_type (str): ビルドのタイプ
        """
        self.score = sum([status.get_score(build_type)
                         for status in self.status])


class Weapon(BaseModel):
    name: str
    icon_name: str
    main_name: str
    main_value: str
    sub_name: str
    sub_value: str
    icon: str
    level: int
    rank: int


class Skill(BaseModel):
    name: str
    icon: str
    level: int
    add_level: int


class Character(BaseModel):
    id: str
    name: str
    english_name: str
    image: str
    element: str
    star: int
    constellations: str
    level: str
    love: int
    base_hp: str
    added_hp: str
    base_attack: str
    added_attack: str
    base_defense: str
    added_defense: str
    critical_rate: str
    critical_damage: str
    charge_efficiency: str
    elemental_mastery: str
    elemental_name: str = None
    elemental_value: str = None
    skills: list[Skill]
    artifacts: dict[str, Artifact]
    weapon: Weapon
    uid: int
    create_date: str
    build_type: str = None

    def get_dir(self):
        if self.english_name == "Player":
            return f"{self.english_name}/{self.element}"
        return self.english_name

    def set_build_type(self, build_type: str):
        self.build_type = build_type.replace(" ver2", "")
        for artifact in self.artifacts.values():
            artifact.calc_score(build_type)


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
