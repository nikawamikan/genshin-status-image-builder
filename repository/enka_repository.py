import lib.downloader as downloader
from model.enka_model import Enka


async def get_enka_model(uid: int):

    data = await downloader.json_download(
        url=f"https://enka.network/api/uid/{uid}"
    )
    try:
        enka_model = Enka(** data)
    except:
        print(data)
        with open(f"error/error{uid}.json", "w") as f:
            f.write(data)
    return enka_model
