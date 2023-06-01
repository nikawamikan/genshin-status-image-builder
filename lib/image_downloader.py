import aiohttp
import json
import aiofiles
import asyncio
from aiohttp import client_exceptions
from lib.httpheader import HEADERS
import os

INTERVAL = 30


class ExcludeFiles:
    def __init__(self, file_name: str = "data/exclude_file.json"):
        self.file_name = file_name
        exclude_set = set()
        try:
            with open(self.file_name, "r") as f:
                data = json.loads(f.read())
                for v in data["exclude_list"]:
                    exclude_set.add(v)
        except:
            pass
        self.exclude_set = exclude_set

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        with open(self.file_name, "w") as f:
            f.write(json.dumps(
                {"exclude_list": list(self.exclude_set)},
                ensure_ascii=False,
            ))


async def image_download(url: str, path: str):
    async with aiohttp.ClientSession(raise_for_status=True, headers=HEADERS) as session:
        async with session.get(url) as response:
            async with aiofiles.open(path, mode="wb") as f:
                await f.write(await response.read())
                print(f"download -> url: {url}, path: {path}")


async def image_download_404_exclusion(url: str, path: str, exclude_set: set[str]) -> bool:
    if url in exclude_set:
        return False
    try:
        await image_download(url, path)
    except client_exceptions.ClientResponseError as e:
        if e.status == 404:
            exclude_set.add(url)
            return False
        else:
            raise e
    return True


def filter_exists_files(url_and_paths: list[tuple[str, str]]) -> list[tuple[str, str]]:
    return [
        (url, path)
        for url, path in url_and_paths
        if not os.path.isfile(path)
    ]


def mkdirs(paths: list[str]):
    dirs = set(["/".join(v.split("/")[:-1]) for v in paths])
    for v in dirs:
        print(v)
        os.makedirs(v, exist_ok=True)


async def images_update(url_and_paths: list[tuple[str, str]]):
    _url_and_paths = filter_exists_files(url_and_paths)
    mkdirs([v[1] for v in _url_and_paths])
    with ExcludeFiles() as exclude:
        for url, path in _url_and_paths:
            if await image_download_404_exclusion(url, path, exclude_set=exclude.exclude_set):
                await asyncio.sleep(INTERVAL)
