from model.response_json_model import CharacterPosition, Position
import repository.util_repository as util_repo
from lib.json_lib import save_json


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
    positions = util_repo.get_position_model_dict()
    if english_name not in positions:
        positions[english_name] = {}
    positions[english_name][costume_id] = position
    save_json(path="data/positions.json",
              obj={k: {k2: v2.dict() for k2, v2 in v.items()} for k, v in positions.items()})


def position_update():
    chara_data = util_repo.CHARACTER_DATA_DICT
    position_data = util_repo.get_position_model_dict()
    for character in chara_data.values():
        if character.english_name not in position_data:
            continue

        for costume_id in character.costumes.keys():
            if costume_id not in position_data[character.english_name]:
                continue

            character.costumes[costume_id].position = position_data[character.english_name][costume_id]
    save_json(
        path="data/characters.json",
        obj={k: v.dict() for k, v in chara_data.items()}
    )
