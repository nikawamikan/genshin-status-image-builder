import repository.util_data as util_data
import json
import asyncio
from model.enka_model import Enka
from service.enka_image_downloader import util_image_update

# async def test():
#     print(await util_data.get_namehash_model_dict())
# asyncio.run(test())


# with open("data/enka.json", "r") as f:
#     data = json.loads(f.read())


# print(Enka(**data).playerInfo)

asyncio.run(util_image_update())
