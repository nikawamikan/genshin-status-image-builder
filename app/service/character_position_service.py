from model.response_json_model import CharacterPosition, Position
import repository.util_repository as util_repo
from lib.async_json import save_json


class Set(set):
    def add(self, __element):
        """値が追加されたかをboolで返却するaddです

        Args:
            __element (any): setの__elementと同じ扱い

        Returns:
            bool: 値が追加されたか
        """
        if __element in self:
            return False
        super().add(__element)
        return True


async def get_character_positions():
    check_set = Set()
    return [
        CharacterPosition(
            id=id,
            name=character.name,
            english_name=character.english_name,
            costume_id=costume_id,
            costume_icon_url=f"https://enka.network/ui/{costume.gacha_icon.name}",
            position=costume.position,
        )
        for id, character in util_repo.CHARACTER_DATA_DICT.items() for costume_id, costume in character.costumes.items()
        if check_set.add(character.english_name+costume_id)
    ]


async def update_position_data(english_name: str, costume_id: str, position: Position):
    positions = await util_repo.get_position_model_dict()
    if english_name not in positions:
        positions[english_name] = Position()
    positions[english_name][costume_id] = position
    await save_json(path="data/positions.json", obj={k: {k2: v2.dict() for k2, v2 in v.items()} for k, v in positions.items()})
