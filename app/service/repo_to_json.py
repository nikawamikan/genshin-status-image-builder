from model.git_model import ArtifactModel, ArtifactSetNameModel,  WeaponModel, CharacterConfigModel
from model.util_model import Artifact, Weapon, NameCard, Costume, Skill, Icon,  JpCharacterModel, Position
from lib.json_lib import save_json
import repository.git_repository as git_repo
import repository.util_repository as util_repository


NAME_SUBSTR = len("UI_AvatarIcon_Side_")


async def save_json_file(file_name: str, obj: dict):
    save_json(f"data/{file_name}", obj)


async def weapon_dict_builder(
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

    weapon_models = [
        v for v in weapon_models
        if v.storyId is not None
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


async def artifact_dict_builder(
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


async def get_jp_character_models(
    config_model: dict[str, CharacterConfigModel],
    jp_name: dict[str, str]
) -> dict[str, JpCharacterModel]:

    def check_none_dict(data: dict, *keys: str):
        if keys[0] in data:
            if len(keys) == 1:
                return data[keys[0]]
            return check_none_dict(data[keys[0]], *keys[1:])
        else:
            return Position()

    position_data = util_repository.get_position_model_dict()
    result = {}
    skill_names = ["通常攻撃",  "元素スキル", "元素爆発"]
    for k, v in config_model.items():
        name = v.SideIconName[NAME_SUBSTR:]
        base_path = f"image/character/{name}/"
        skill_path = f"{base_path}skill/"
        consts_path = f"{base_path}consts/"
        avatar_icon = f"UI_AvatarIcon_{name}.png"
        gacha_icon = f"UI_Gacha_AvatarImg_{name}.png"
        chara_icon_path = f"{base_path}avatar/"
        chara_icon_path_default = f"{chara_icon_path}default/"
        costume = {
            k: Costume(
                avatar_icon=Icon(
                    name=f'{v.icon}.png',
                    path=f'{chara_icon_path}{k}/{v.icon}.png'
                ),
                side_icon=Icon(
                    name=f'{v.sideIconName}.png',
                    path=f'{chara_icon_path}{k}/{v.sideIconName}.png'
                ),
                gacha_icon=Icon(
                    name=f'{v.art}.png',
                    path=f'{chara_icon_path}{k}/{v.art}.png'
                ),
                position=check_none_dict(
                    position_data,
                    name,
                    k
                )
            ) for k, v in v.Costumes.items()
        }
        costume["default"] = Costume(
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
            position=check_none_dict(
                position_data,
                name,
                "default",
            )
        )
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
                    name=skill_names[i],
                    icon=Icon(
                        name=f"{v.Skills[v2]}.png",
                        path=f"{skill_path}{v.Skills[v2]}.png"
                    ),
                    id=v2,
                    proud_id=v.ProudMap[v2]
                )for i, v2 in enumerate(v.SkillOrder)
            ],
            name=jp_name[v.NameTextMapHash],
            english_name=name,
            proud_map=v.ProudMap,
            quality=5 if v.QualityType == "QUALITY_ORANGE" else 4,
            costumes=costume,
        )
        result[k] = data

    return result


async def updates(debug_flg: bool = False):
    """gihhubよりAPIに必要なデータの構築を行い保存する処理を行います。
    """

    # 更新の必要性を確認します
    if not git_repo.confirmation_update_necessity() and not debug_flg:
        print("no update")
        return False

    artifact_models = await git_repo.get_artifact_dict()
    artifact_set_name_models = await git_repo.get_artifact_set_name_dict()
    weapon_models = await git_repo.get_weapon_dict()
    names = await git_repo.get_name_dict()
    characters = await git_repo.get_character_dict()
    namecards = await git_repo.get_namecard_dict()

    # 聖遺物情報を扱いやすい形に変換
    artifact_dict = await artifact_dict_builder(
        artifact_models=artifact_models,
        artifact_name_models=artifact_set_name_models,
        enka_names=names["ja"],
    )

    # 武器情報を扱いやすい形に変換
    weapon_dict = await weapon_dict_builder(
        weapon_models=weapon_models,
        enka_names=names["ja"]
    )

    # キャラクター情報を扱いやすい形に変換
    character_dict = await get_jp_character_models(
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

    return True
