from model.git_model import ArtifactModel, ArtifactSetNameModel,  WeaponModel, CharacterConfigModel
from model.util_model import Artifact, Weapon, NameCard, Costume, Skill, Icon,  JpCharacterModel
from lib.async_json import save_json
import repository.git_repository as git_repo
import os

NAME_SUBSTR = len("UI_AvatarIcon_Side_")


async def save_json_file(file_name: str, obj: dict):
    await save_json(f"data/{file_name}", obj)


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

    # 更新の必要性を確認します
    if not git_repo.confirmation_update_necessity():
        print("no update")
        return

    artifact_models = await git_repo.get_artifact_dict()
    artifact_set_name_models = await git_repo.get_artifact_set_name_dict()
    weapon_models = await git_repo.get_weapon_dict()
    names = await git_repo.get_name_dict()
    characters = await git_repo.get_character_dict()
    namecards = await git_repo.get_namecard_dict()

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

    git_repo.save_last_push_dates()
