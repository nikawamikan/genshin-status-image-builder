from io import BytesIO
from lib.gen_image import GImage, Colors, Algin, Anchors, ImageAnchors
from concurrent.futures import ThreadPoolExecutor, Future
import os
import model.status_model as status_model
import model.util_model as util_model
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance
from repository.assets_repository import ASSETS
from decimal import Decimal
import lib.cache_image as cache_image
from collections import Counter

cwd = os.path.abspath(os.path.dirname(__file__))

BASE_SIZE = (840, 400)

def __create_background(userdata: status_model.UserData):
    """バックグラウンドを生成します。

    Args:
        UserData (status_model.UserData): ユーザーデータ

    Returns:
        GImage: 合成した画像
    """
    bg = GImage(box_size=BASE_SIZE)
    bg.add_image(userdata.name_card.icon.path, size=BASE_SIZE)
    bg.add_image(ASSETS.profile.layer)
    
    # Image→GImageに変換

    return bg

def __create_profile(userdata: status_model.UserData):
    """基本情報を生成します。

    Args:
        UserData (status_model.UserData): ユーザーデータ

    Returns:
        GImage: 合成した画像
    """
    bg = GImage(box_size=BASE_SIZE)
    bg.draw_text(text=f'UID:{userdata.uid}', position=(40, 41), font_size=21, anchor=Anchors.LEFT_MIDDLE)
    bg.draw_text(text=f'{userdata.nickname}', position=(254, 154), font_size=54, anchor=Anchors.LEFT_MIDDLE)
    bg.draw_text(text=f'{userdata.signature}', position=(260, 197), font_size=18, anchor=Anchors.LEFT_MIDDLE)
    return bg.get_image()

def __create_icon(userdata: status_model.UserData):
    """アイコン画像を生成します。

    Args:
        UserData (status_model.UserData): ユーザーデータ

    Returns:
        GImage: 合成した画像
    """
    bg = Image.new("RGBA", size=(190, 190))
    mask = Image.new("L", (190, 190), 0)
    icon = Image.open(userdata.profile_picture.avatar_icon.path).convert("RGBA").resize((190, 190))
    fix_mask = icon.copy()

    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, 190, 190), fill=255)
    im = Image.composite(icon, bg, mask)
    bg.paste(im, (0, 0), mask=fix_mask)

    # Image→GImageに変換

    return bg
    
def __create_data_list(userdata: status_model.UserData):
    """詳細情報を生成します。

    Args:
        UserData (status_model.UserData): ユーザーデータ

    Returns:
        GImage: 合成した画像
    """
    bg = GImage(box_size=BASE_SIZE)
    bg.draw_text(text=f'{userdata.level}', position=(22, 350), font_size=45, anchor=Anchors.LEFT_MIDDLE)
    bg.draw_text(text=f'{userdata.world_level}', position=(237, 350), font_size=45, anchor=Anchors.LEFT_MIDDLE)
    bg.draw_text(text=f'{userdata.tower_floor_index}-{userdata.tower_level_index}', position=(440, 350), font_size=45, anchor=Anchors.LEFT_MIDDLE)
    bg.draw_text(text=f'{userdata.finish_achievement_num}', position=(649, 350), font_size=45, anchor=Anchors.LEFT_MIDDLE)
    return bg.get_image()

def __create_image(userdata: status_model.UserData) -> Image.Image:
    """ユーザーデータから画像を生成します。

    Args:
        userdata (UserData): ユーザーデータ

    Returns:
        Image.Image: キャラ画像
    """
    
    with ThreadPoolExecutor(thread_name_prefix="__create") as pool:
        # 背景画像の取得
        bgf: Future = pool.submit(
            __create_background,
            userdata=userdata,
        )

        # 基本情報画像を取得
        profilef: Future = pool.submit(
            __create_profile, userdata)

        # アイコンを取得
        iconf: Future = pool.submit(
            __create_icon,
            userdata,
        )

        # 詳細情報画像の取得
        dataf: Future = pool.submit(
            __create_data_list,
            userdata,
        )

    # 各リザルトを取得
    bg = bgf.result()
    profile = profilef.result()
    icon = iconf.result()
    data = dataf.result()

    bg.paste(im=profile)
    bg.paste(
        im=icon,
        box=(35, 172),
        image_anchor=ImageAnchors.LEFT_MIDDLE
    )
    bg.paste(im=data)
    
    return bg.get_image()

def save_image(file_path: str, userdata: status_model.UserData):
    if cache_image.check_cache_exists(file_path=file_path):
        return

    userdata.set_namecard()
    image = __create_image(userdata=userdata)
    image = image.convert("RGB")
    image.save(file_path, optimize=True, quality=100)
    cache_image.cache_append(file_path=file_path)

