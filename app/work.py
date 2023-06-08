from lib.async_json import load_json, save_json
import asyncio
from repository.util_repository import CHARACTER_DATA_DICT
from model.util_model import Position


async def main():
    data: dict[str, dict[str, Position]] = {}
    for k, v in CHARACTER_DATA_DICT.items():
        data[v.english_name] = {costume_id: costume.position for costume_id,
                                costume in v.costumes.items()}

    await save_json("data/position.json", {k: {k2: v2.dict() for k2, v2 in v.items()} for k, v in data.items()})

    length = sum([len(v) for v in data.values()])
    x = sum([v2.x for v in data.values() for v2 in v.values()])/length
    y = sum([v2.y for v in data.values() for v2 in v.values()])/length
    z = sum([v2.scale for v in data.values() for v2 in v.values()])/length

    print("ave", x, y, z)
asyncio.run(main())
