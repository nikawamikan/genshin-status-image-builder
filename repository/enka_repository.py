import lib.downloader as downloader
from model.enka_model import PlayerInfo


async def get_enka_model(uid: int):
    enka_model = PlayerInfo(** await downloader.json_download(
        url=f"https://enka.network/api/uid/{uid}"
    ))
    return enka_model
