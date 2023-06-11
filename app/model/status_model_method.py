from decimal import Decimal
from model.status_model import ArtifactStatus, Artifact, Weapon, Skill, Character, UserData
import service.score_calc as score_calc
import model.util_model as util_model
from repository.util_repository import \
    CHARACTER_DATA_DICT, WEAPON_DATA_DICT, ARTIFACT_DATA_DICT, STATUS_NAMEHASH_DICT
from service.score_calc import BUILD_NAMES


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


class ArtifactStatusMethod(ArtifactStatus):
    @property
    def jp_name(self):
        return STATUS_NAMEHASH_DICT[self.name]

    @property
    def value_str(self):
        return get_status_base(self.value, self.suffix)

    def get_score(self, calc: score_calc.ScoreCalc):
        return calc.calc(self.name, self.value)


class ArtifactMethod(Artifact):
    status: list[ArtifactStatusMethod]

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


class WeaponMethod(Weapon):

    @property
    def main_jp_name(self):
        return STATUS_NAMEHASH_DICT[self.main_name]

    @property
    def sub_jp_name(self):
        return STATUS_NAMEHASH_DICT[self.sub_name]

    def set_util(self):
        self.util = WEAPON_DATA_DICT[self.icon_name]


class SkillMethod(Skill):

    def set_util(self, skill: util_model.Skill):
        self.util = skill


class CharacterMethod(Character):
    skills: list[SkillMethod]
    artifacts: dict[str, ArtifactMethod]
    weapon: WeaponMethod

    @property
    def build_name(self):
        return BUILD_NAMES[self.build_type]

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

    def set_build_type(self, build_type: str):
        self.build_type = build_type
        calc = score_calc.ScoreCalc(build_type)
        for artifact in self.artifacts.values():
            artifact.set_calc_score(calc)


class UserDataMethod(UserData):
    characters: list[CharacterMethod]
