from decimal import Decimal

CRITICAL = "会心率"
CRITICAL_HURT = "会心ダメ"
ATTACK_PERCENT = "攻撃力%"
CHARGE_EFFICIENCY = "元チャ効率"
DEFENSE_PERCENT = "防御力%"
HP_PERCENT = "HP%"
ELEMENT_MASTERY = "元素熟知"

BUILD_NAMES = {
    "atk":ATTACK_PERCENT,
    "ch":CHARGE_EFFICIENCY,
    "def":DEFENSE_PERCENT,
    "hp":HP_PERCENT,
    "em":ELEMENT_MASTERY,
    "def2": f"{DEFENSE_PERCENT} ver2",
    "ch2": f"{CHARGE_EFFICIENCY} ver2",
    "em2": f"{ELEMENT_MASTERY} ver2",
}


def calc(status_type: str, value: float, build_type: str):
    result = Decimal(0)

    if status_type == CRITICAL:  # 会心率（2倍）
        result = Decimal(value) * Decimal(2)
    elif status_type == CRITICAL_HURT:  # 会心ダメ
        result = Decimal(value)
    elif status_type == CHARGE_EFFICIENCY and build_type == f"{CHARGE_EFFICIENCY} ver2":
        result = Decimal(value) * Decimal(0.9)
    elif status_type == DEFENSE_PERCENT and build_type == f"{DEFENSE_PERCENT} ver2":
        result = Decimal(value) * Decimal(0.8)
    elif status_type == ELEMENT_MASTERY and build_type == f"{ELEMENT_MASTERY} ver2":
        result = Decimal(value) * Decimal(0.25)
    elif status_type == build_type:
        result = Decimal(value)
        
    if build_type == ELEMENT_MASTERY:
        result /= Decimal(2)
        
    return result

# 元素チャージ → Ch: 1, 率: 2, ダメ: 1
# 防御 →  防御率: 1, 率: 2, ダメ: 1
# HP型 → HP: 1, 率:2, ダメ: 1
# 熟知型 → 元素熟知: 1/2, 率: 1, ダメ: 1/2
