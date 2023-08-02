import json
from typing import Union


def save_json(path: str, obj: dict):
    """jsonデータを保存します

    Args:
        path (str): ファイルのパス
        obj (dict): jsonとして保存するdict
    """
    with open(path, "w") as f:
        f.write(
            json.dumps(
                obj,
                ensure_ascii=False,
                indent=4,
            )
        )


def load_json(path: str) -> Union[dict, list]:
    """jsonのファイルを読み込みます。

    Args:
        path (str): ファイルのパス

    Returns:
        Union[dict, list]: listまたはdictで構成されるjsonデータ
    """
    with open(path, "r") as f:
        return json.loads(f.read())
