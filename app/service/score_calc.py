from decimal import Decimal


ATK = "atk"
CH = "ch"
DEF = "def"
HP = "hp"
EM = "em"
CH2 = "ch2"
DEF2 = "def2"
EM2 = "em2"

BUILD_NAMES = {
    ATK: "攻撃力%",
    CH: "原チャ効率",
    DEF: "防御力%",
    HP: "HP%",
    EM: "元素熟知",
    CH2: "原チャ効率",
    DEF2:  "防御力%",
    EM2: "元素熟知",
}


FIGHT_PROP_CRITICAL = "FIGHT_PROP_CRITICAL"  # 会心率
FIGHT_PROP_CRITICAL_HURT = "FIGHT_PROP_CRITICAL_HURT"  # 会心ダメ
FIGHT_PROP_ATTACK_PERCENT = "FIGHT_PROP_ATTACK_PERCENT"  # 攻撃%
FIGHT_PROP_CHARGE_EFFICIENCY = "FIGHT_PROP_CHARGE_EFFICIENCY"  # チャージ効率
FIGHT_PROP_DEFENSE_PERCENT = "FIGHT_PROP_DEFENSE_PERCENT"  # 防御%
FIGHT_PROP_HP_PERCENT = "FIGHT_PROP_HP_PERCENT"  # HP%
FIGHT_PROP_ELEMENT_MASTERY = "FIGHT_PROP_ELEMENT_MASTERY"  # 元素熟知

SCORE_FORMULA_DICT = {
    ATK: {
        FIGHT_PROP_CRITICAL: Decimal(2),
        FIGHT_PROP_CRITICAL_HURT: Decimal(1),
        FIGHT_PROP_ATTACK_PERCENT: Decimal(1),
    },
    CH: {
        FIGHT_PROP_CRITICAL: Decimal(2),
        FIGHT_PROP_CRITICAL_HURT: Decimal(1),
        FIGHT_PROP_CHARGE_EFFICIENCY: Decimal(1),
    },
    DEF: {
        FIGHT_PROP_CRITICAL: Decimal(2),
        FIGHT_PROP_CRITICAL_HURT: Decimal(1),
        FIGHT_PROP_DEFENSE_PERCENT: Decimal(1)
    },
    HP: {
        FIGHT_PROP_CRITICAL: Decimal(2),
        FIGHT_PROP_CRITICAL_HURT: Decimal(1),
        FIGHT_PROP_HP_PERCENT: Decimal(1)
    },
    EM: {
        FIGHT_PROP_CRITICAL: Decimal(1),
        FIGHT_PROP_CRITICAL_HURT: Decimal(0.5),
        FIGHT_PROP_ELEMENT_MASTERY: Decimal(0.5),
    },
    CH2: {
        FIGHT_PROP_CRITICAL: Decimal(2),
        FIGHT_PROP_CRITICAL_HURT: Decimal(1),
        FIGHT_PROP_CHARGE_EFFICIENCY: Decimal(0.9),
    },
    DEF2: {
        FIGHT_PROP_CRITICAL: Decimal(2),
        FIGHT_PROP_CRITICAL_HURT: Decimal(1),
        FIGHT_PROP_DEFENSE_PERCENT: Decimal(0.8),
    },
    EM2: {
        FIGHT_PROP_CRITICAL: Decimal(2),
        FIGHT_PROP_CRITICAL_HURT: Decimal(1),
        FIGHT_PROP_ELEMENT_MASTERY: Decimal(0.25),
    },
}


class ScoreCalc:
    def __init__(self, build_type: str):
        _build_type = {}
        if build_type in SCORE_FORMULA_DICT:
            _build_type = SCORE_FORMULA_DICT[build_type]
        self.build_type = _build_type

    def calc(self, status_type: str, value: Decimal):
        result = Decimal(0)
        if status_type in self.build_type:
            result = self.build_type[status_type] * Decimal(value)
        return result

# 元素チャージ → Ch: 1, 率: 2, ダメ: 1
# 防御 →  防御率: 1, 率: 2, ダメ: 1
# HP型 → HP: 1, 率:2, ダメ: 1
# 熟知型 → 元素熟知: 1/2, 率: 1, ダメ: 1/2
# 元素チャージ2 → 0.9, 率: 2, ダメ: 1
# 防御2 → 防御 0.8, 率: 2, ダメ: 1
# 熟知型 → 元素熟知 1/4, 率: 2, ダメ: 1
