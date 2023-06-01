from github import Github, Repository
import aiohttp
import json
import datetime
from model.git_model import ArtifactModel, ArtifactSetNameModel,  WeaponModel, CharacterConfigModel
from model.util_model import Artifact, Weapon, NameCard, Costume, Skill, Icon,  JpCharacterModel
from lib.model_converter import conversion_dict_to_model, conversion_list_to_model
from lib.httpheader import HEADERS
from lib.async_json import save_json
import os

INTERVAL = 10
GITHUB = Github(os.getenv("GIT_TOKEN"))
GENSHIN_DATA_REPO_NAME = "Sycamore0/GenshinData"
ENKA_DATA_REPO_NAME = "EnkaNetwork/API-docs"
NAME_SUBSTR = len("UI_AvatarIcon_Side_")


async def save_json_file(file_name: str, obj: dict):
    await save_json(f"data/{file_name}", obj)


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


def get_repo(repo_name: str) -> Repository.Repository:
    """リポジトリを取得します

    Args:
        repo_name (str): リポジトリ名

    Returns:
        Repository: リポジトリ
    """
    return GITHUB.get_repo(repo_name)


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


def last_push_date_checker(
    criteria_date: datetime.datetime,
    updated_date: datetime.datetime
) -> bool:
    """日付から更新が必要かチェックします

    Args:
        criteria_date (datetime.datetime): 基準日
        updated_date (datetime.datetime): 更新日

    Returns:
        bool: 更新の必要性
    """
    return criteria_date < updated_date


def load_last_push_dates() -> dict[str, datetime.datetime]:
    """基準となる日付をロードします。

    Returns:
        dict[str, datetime.datetime]: リポジトリ名に紐付けられた更新日
    """
    with open("lastpushdate.json", "r") as f:
        d: dict[str, str] = json.loads(f.read())
    return {k: datetime.datetime.fromisoformat(v) for k, v in d.items()}


def last_push_date_checker_iter(
    keys: list[str],
    criteria_dates: list[datetime.datetime],
    updated_dates: list[datetime.datetime]
) -> dict[str, bool]:
    """それぞれの更新日をチェックし更新の必要性があるかをdictで返却します。

    Args:
        keys (list[str]): リポジトリ名
        criteria_dates (list[datetime.datetime]): 基準日
        updated_dates (list[datetime.datetime]): 更新日

    Returns:
        dict[str, bool]: リポジトリ名に紐付けられた更新の必要性
    """
    return {
        key: last_push_date_checker(criteria_date, updated_date)
        for key, criteria_date, updated_date in zip(keys, criteria_dates, updated_dates)
    }


def weapon_dict_builder(
    weapon_models: list[WeaponModel],
    enka_names: list[str, str]
) -> dict[str, Weapon]:
    """武器の情報を扱いやすくします

    Args:
        weapon_models (list[WeaponModel]): 生の武器データ
        enka_names (list[str, str]): 名称のデータ

    Returns:
        dict[str, Weapon]: idに紐付けられた武器情報
    """
    weapon_models = [
        v for v in weapon_models
        if v.nameTextMapHash in enka_names
    ]

    return {
        v.icon: Weapon(
            icon=Icon(
                name=f"{v.icon}.png",
                path=f"image/weapon/{v.icon}.png"
            ),
            name=enka_names[v.nameTextMapHash],
        ) for v in weapon_models
    }


def unique_artifact_list(artifact_models: list[ArtifactModel]) -> list[ArtifactModel]:
    """聖遺物情報を一意にします

    Args:
        artifact_models (list[ArtifactModel]): 生の聖遺物情報

    Returns:
        list[ArtifactModel]: 一意に変換された聖遺物情報
    """
    icon_name_set = set()
    result = []
    for v in artifact_models:
        if v.setId is not None and v.icon not in icon_name_set:
            icon_name_set.add(v.icon)
            result.append(v)
    for v in artifact_models:
        if v.icon not in icon_name_set:
            result.append(v)
            icon_name_set.add(v.icon)
    return result


def artifact_dict_builder(
    artifact_models: list[ArtifactModel],
    artifact_name_models: list[ArtifactSetNameModel],
    enka_names: list[str, str]
) -> dict[str, Artifact]:
    """聖遺物情報を扱いやすく変換します。

    Args:
        artifact_models (list[ArtifactModel]): 生の聖遺物情報
        artifact_name_models (list[ArtifactSetNameModel]): 聖遺物のセット名を取得するための情報
        enka_names (list[str, str]): 名称のデータ

    Returns:
        dict[str, Artifact]: 聖遺物の名称で紐づけされた聖遺物情報
    """
    artifact_models = unique_artifact_list(artifact_models)
    artifact_name_dict = {
        v.affixId: v.nameTextMapHash
        for v in artifact_name_models
    }
    for v in artifact_models:
        s = artifact_name_dict.get(f"2{v.setId}1")
        if s is not None:
            v.nameTextMapHash = str(s)

    return {
        v.icon: Artifact(
            icon=Icon(
                name=f"{v.icon}.png",
                path=f"image/artifact/{v.icon}.png"
            ),
            set_name=enka_names.get(v.nameTextMapHash),
            equip_type=v.equipType,
        ) for v in artifact_models
    }


def namecard_dict_builder(namecards: dict[str, str]):
    return {
        k: NameCard(
            icon=Icon(
                name=f"{v}.png",
                path=f"image/namecard/{v}.png"
            )
        ) for k, v in namecards.items()
    }


def get_jp_character_models(
    config_model: dict[str, CharacterConfigModel],
    jp_name: dict[str, str]
) -> dict[str, JpCharacterModel]:
    result = {}
    for k, v in config_model.items():
        name = v.SideIconName[NAME_SUBSTR:]
        base_path = f"image/character/{name}/"
        skill_path = f"{base_path}skill/"
        consts_path = f"{base_path}consts/"
        avatar_icon = f"UI_AvatarIcon_{name}.png"
        gacha_icon = f"UI_Gacha_AvatarImg_{name}.png"
        chara_icon_path = f"{base_path}avatar/"
        chara_icon_path_default = f"{chara_icon_path}default/"
        data = JpCharacterModel(
            element=v.Element,
            consts=[
                Icon(
                    name=f"{v2}.png",
                    path=f"{consts_path}{v2}.png"
                )
                for v2 in v.Consts
            ],
            skills=[
                Skill(
                    icon=Icon(
                        name=f"{v.Skills[v2]}.png",
                        path=f"{skill_path}{v.Skills[v2]}.png"
                    ),
                    id=v2,
                    proud_id=v.ProudMap[v2]
                )for v2 in v.SkillOrder
            ],
            name=jp_name[v.NameTextMapHash],
            english_name=name,
            proud_map=v.ProudMap,
            quality=5 if v.QualityType == "QUALITY_ORANGE" else 4,
            avatar_icon=Icon(
                name=avatar_icon,
                path=f"{chara_icon_path_default}{avatar_icon}"
            ),
            side_icon=Icon(
                name=f"{v.SideIconName}.png",
                path=f"{chara_icon_path_default}{v.SideIconName}.png"
            ),
            gacha_icon=Icon(
                name=gacha_icon,
                path=f"{chara_icon_path_default}{gacha_icon}"
            ),
            costumes={
                k2: Costume(
                    avatar_icon=Icon(
                        name=f'{v2.icon}.png',
                        path=f'{chara_icon_path}{k2}/{v2.icon}.png'
                    ),
                    side_icon=Icon(
                        name=f'{v2.sideIconName}.png',
                        path=f'{chara_icon_path}{k2}/{v2.sideIconName}.png'
                    ),
                    gacha_icon=Icon(
                        name=f'{v2.art}.png',
                        path=f'{chara_icon_path}{k2}/{v2.art}.png'
                    ),
                ) for k2, v2 in v.Costumes.items()
            },
        )
        result[k] = data
    return result


async def updates():
    """gihhubよりAPIに必要なデータの構築を行い保存する処理を行います。
    """

    # 前回の更新日時を読み込み
    criteria_date_dict = load_last_push_dates()

    # リポジトリをdictとしてインスタンス化
    repos = get_repo_dict(
        GENSHIN_DATA_REPO_NAME,
        ENKA_DATA_REPO_NAME
    )

    # リポジトリの更新日時取得
    repo_push_dates = {key: repo.pushed_at for key, repo in repos.items()}

    # 更新が必要かの情報を取得
    update_necessity_dict = last_push_date_checker_iter(
        repo_push_dates.keys(),
        [
            criteria_date_dict[key] for key in repo_push_dates.keys()
        ],
        repo_push_dates.values()
    )

    # どちらも更新がない場合は処理を終了させる
    if True not in tuple(update_necessity_dict.values()):
        print("no update")
        return

    # 聖遺物の情報の取得
    artifact_models = conversion_list_to_model(
        await git_json_download(
            repos[GENSHIN_DATA_REPO_NAME].get_contents(
                "ExcelBinOutput/ReliquaryExcelConfigData.json"
            ).download_url
        ),
        ArtifactModel
    )

    # 聖遺物のセット名が紐付けられたデータの取得
    artifact_set_name_models = conversion_list_to_model(
        await git_json_download(
            repos[GENSHIN_DATA_REPO_NAME].get_contents(
                "ExcelBinOutput/EquipAffixExcelConfigData.json"
            ).download_url
        ),
        ArtifactSetNameModel
    )

    # 武器の情報の取得
    weapon_models = conversion_list_to_model(
        await git_json_download(
            repos[GENSHIN_DATA_REPO_NAME].get_contents(
                "ExcelBinOutput/WeaponExcelConfigData.json"
            ).download_url
        ),
        WeaponModel
    )

    # 名称の一覧を取得
    names = await git_json_download(
        repos[ENKA_DATA_REPO_NAME].get_contents("store/loc.json").download_url
    )

    # 名札の情報を取得
    namecards = {
        k: v["icon"]
        for k, v in (await git_json_download(
            repos[ENKA_DATA_REPO_NAME].get_contents(
                "store/namecards.json"
            ).download_url
        )).items()
    }

    # キャラクター情報の取得
    characters = conversion_dict_to_model(
        await git_json_download(
            repos[ENKA_DATA_REPO_NAME].get_contents(
                "store/characters.json"
            ).download_url
        ),
        CharacterConfigModel
    )

    # 聖遺物情報を扱いやすい形に変換
    artifact_dict = artifact_dict_builder(
        artifact_models=artifact_models,
        artifact_name_models=artifact_set_name_models,
        enka_names=names["ja"],
    )

    # 武器情報を扱いやすい形に変換
    weapon_dict = weapon_dict_builder(
        weapon_models=weapon_models,
        enka_names=names["ja"]
    )

    # キャラクター情報を扱いやすい形に変換
    character_dict = get_jp_character_models(
        config_model=characters,
        jp_name=names["ja"]
    )

    namecard_dict = namecard_dict_builder(namecards=namecards)

    # 各情報をjsonとして保存します
    await save_json_file("artifacts.json", {k: v.dict() for k, v in artifact_dict.items()})
    await save_json_file("weapons.json", {k: v.dict() for k, v in weapon_dict.items()})
    await save_json_file("namecards.json", {k: v.dict() for k, v in namecard_dict.items()})
    await save_json_file("names.json", names["ja"])
    await save_json_file("characters.json", {k: v.dict() for k, v in character_dict.items()})
