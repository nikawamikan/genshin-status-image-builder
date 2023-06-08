import repository.util_repository as util_repository
from lib.downloader import images_update
from model.util_model import Icon


def get_url_and_path(icon: Icon):
    return (f"https://enka.network/ui/{icon.name}", icon.path)


def get_url_and_paths(obj):
    return [
        get_url_and_path(v.icon)
        for v in obj.values()
    ]


async def util_image_update():
    weapons = await util_repository.get_weapon_model_dict()
    artifacts = await util_repository.get_artfact_model_dict()
    namecades = await util_repository.get_namecard_model_dict()
    characters = await util_repository.get_character_model_dict()
    charcter_urlpaths = []
    for character in characters.values():
        for costume in character.costumes.values():
            charcter_urlpaths.append(get_url_and_path(costume.avatar_icon))
            charcter_urlpaths.append(get_url_and_path(costume.side_icon))
            charcter_urlpaths.append(get_url_and_path(costume.gacha_icon))
        for skill in character.skills:
            charcter_urlpaths.append(get_url_and_path(skill.icon))
        for const in character.consts:
            charcter_urlpaths.append(get_url_and_path(const))
    url_and_paths = get_url_and_paths(weapons) + get_url_and_paths(
        artifacts) + get_url_and_paths(namecades) + charcter_urlpaths

    await images_update(url_and_paths)
