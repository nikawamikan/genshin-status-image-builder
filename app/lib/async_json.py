import aiofiles
import json
from typing import Union


async def save_json(path: str, obj: dict):
    """jsonデータを保存します

    Args:
        path (str): ファイルのパス
        obj (dict): jsonとして保存するdict
    """
    async with aiofiles.open(path, "w") as f:
        await f.write(
            json.dumps(
                obj,
                ensure_ascii=False,
                indent=4,
            )
        )


async def load_json(path: str) -> Union[dict, list]:

    """jsonのファイルを読み込みます。

    Args:
        path (str): ファイルのパス

    Returns:
        Union[dict, list]: listまたはdictで構成されるjsonデータ
    """
    async with aiofiles.open(path, "r") as f:
        return json.loads(await f.read())
