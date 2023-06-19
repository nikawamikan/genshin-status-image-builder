from github import Github, Repository
import aiohttp
import json
import datetime
from model.git_model import ArtifactModel, ArtifactSetNameModel,  WeaponModel, CharacterConfigModel
from lib.model_converter import conversion_dict_to_model, conversion_list_to_model
from lib.httpheader import HEADERS
import os


INTERVAL = 10
GITHUB = Github(os.getenv("GIT_TOKEN"))
GENSHIN_DATA_REPO_NAME = "Sycamore0/GenshinData"
ENKA_DATA_REPO_NAME = "EnkaNetwork/API-docs"


REPOS = {}


def get_repo_dict(*repo_names: str) -> dict[str, Repository.Repository]:
    """リポジトリをDict形式で返却します

    Args:
        repo_names (*str): 可変長でリポジトリ名

    Returns:
        dict[str, Repository]: リポジトリ名に紐付けられたリポジトリ
    """
    return {
        repo_name: get_repo(repo_name) for repo_name in repo_names
    }


def get_repo(repo_name: str) -> Repository.Repository:
    """リポジトリを取得します

    Args:
        repo_name (str): リポジトリ名

    Returns:
        Repository: リポジトリ
    """
    return GITHUB.get_repo(repo_name)


def repo_reload():
    global REPOS
    REPOS = get_repo_dict(
        GENSHIN_DATA_REPO_NAME,
        ENKA_DATA_REPO_NAME
    )


async def git_json_download(url: str) -> dict:
    """githubからソースをjson形式で取得します

    Args:
        url (str): githubのdownload_url

    Returns:
        dict: jsonをdict形式に変換したデータ
    """
    async with aiohttp.ClientSession(raise_for_status=True, headers=HEADERS) as session:
        async with session.get(url) as response:
            result = json.loads(await response.text())
    return result


def load_last_push_dates() -> dict[str, datetime.datetime]:
    """基準となる日付をロードします。

    Returns:
        dict[str, datetime.datetime]: リポジトリ名に紐付けられた更新日
    """
    with open("data/lastpushdate.json", "r") as f:
        try:
            d: dict[str, str] = json.loads(f.read())
        except:
            return {
                GENSHIN_DATA_REPO_NAME: datetime.datetime.min,
                ENKA_DATA_REPO_NAME: datetime.datetime.min
            }
    return {k: datetime.datetime.fromisoformat(v) for k, v in d.items()}


def save_last_push_dates() -> dict[str, datetime.datetime]:
    """基準となる日付を保存しますします。

    """
    with open("data/lastpushdate.json", "w") as f:
        global REPOS
        data = {
            k: str(v.pushed_at) for k, v in REPOS.items()
        }
        f.write(json.dumps(data))


def last_push_date_checker() -> bool:
    """それぞれの更新日をチェックし更新の必要性があるか返却

    Returns:
        bool: 更新の必要性を返却します
    """
    global REPOS
    criteria_date_dict = load_last_push_dates()

    return True in [
        (criteria_date < updated_date)
        for criteria_date, updated_date in [
            (criteria_date_dict[k], REPOS[k].pushed_at,)
            for k in REPOS.keys()
        ]
    ]


def confirmation_update_necessity() -> bool:
    """リポジトリの情報を更新し直して更新の必要性があるかをチェックします

    Returns:
        bool: 更新の必要性
    """
    repo_reload()
    return last_push_date_checker()


async def get_artifact_dict():
    return conversion_list_to_model(
        await git_json_download(
            REPOS[GENSHIN_DATA_REPO_NAME].get_contents(
                "ExcelBinOutput/ReliquaryExcelConfigData.json"
            ).download_url
        ),
        ArtifactModel
    )


async def get_artifact_set_name_dict():
    return conversion_list_to_model(
        await git_json_download(
            REPOS[GENSHIN_DATA_REPO_NAME].get_contents(
                "ExcelBinOutput/EquipAffixExcelConfigData.json"
            ).download_url
        ),
        ArtifactSetNameModel
    )


async def get_weapon_dict():
    return conversion_list_to_model(
        await git_json_download(
            REPOS[GENSHIN_DATA_REPO_NAME].get_contents(
                "ExcelBinOutput/WeaponExcelConfigData.json"
            ).download_url
        ),
        WeaponModel
    )


async def get_name_dict():
    return await git_json_download(
        REPOS[ENKA_DATA_REPO_NAME].get_contents("store/loc.json").download_url
    )


async def get_namecard_dict():
    return {
        k: v["icon"]
        for k, v in (await git_json_download(
            REPOS[ENKA_DATA_REPO_NAME].get_contents(
                "store/namecards.json"
            ).download_url
        )).items()
    }


async def get_character_dict():
    return conversion_dict_to_model(
        await git_json_download(
            REPOS[ENKA_DATA_REPO_NAME].get_contents(
                "store/characters.json"
            ).download_url
        ),
        CharacterConfigModel
    )
