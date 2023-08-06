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

BASE_SIZE = (1920, 1080)
TALENT_BASE_SIZE = (int(149/1.5), int(137/1.5))
# TALENT_BACK = Image.open(ASSETS.artifacter.b)
TALENT_BASE = Image.open(
    ASSETS.artifacter.talent_back).resize(TALENT_BASE_SIZE)

CONSTELLATIONBACKS = {
    k: (
        Image.open(v.unlock).resize((90, 90)).convert('RGBA'),
        Image.open(v.lock).resize((90, 90)).convert('RGBA'),
    ) for k, v in ASSETS.artifacter.constellations.items()
}

ARTIFACTER_REFER = {
    "TOTAL": [220, 200, 180],
    "EQUIP_BRACER": [50, 45, 40],
    "EQUIP_NECKLACE": [50, 45, 40],
    "EQUIP_SHOES": [ 45, 40, 35],
    "EQUIP_RING": [45, 40, 37],
    "EQUIP_DRESS": [40, 35, 30]
}

def __create_background(character: status_model.Character):
    """キャラ画像を合成したバックグラウンドを生成します。

    Args:
        character (status_model.Character): キャラデータ

    Returns:
        GImage: 合成した画像
    """
    # 元素別の画像
    bg = GImage(
        ASSETS.artifacter.background[character.util.element]).get_image()
    chara_img = GImage(character.costume.gacha_icon.path).get_image()
    shadow = Image.open(ASSETS.artifacter.shadow).resize(bg.size)
    chara_img = chara_img.crop((289, 0, 1728, 1024))
    chara_img = chara_img.resize(
        (
            int(chara_img.width*0.75),
            int(chara_img.height*0.75)
        )
    )
    chara_mask = chara_img.copy()
    # 偉大なるアルハイゼン様専用処理
    if character.util.english_name == 'Alhaitham':
        mask_path = ASSETS.artifacter.mask.alhaithem
    else:
        mask_path = ASSETS.artifacter.mask.character_mask

    avater_mask = Image.open(mask_path).convert('L').resize(chara_img.size)
    chara_img.putalpha(avater_mask)

    chara_paste = Image.new("RGBA", BASE_SIZE, (255, 255, 255, 0))

    chara_paste.paste(chara_img, (-160, -45), mask=chara_mask)
    bg = Image.alpha_composite(bg, chara_paste)
    bg = Image.alpha_composite(bg, shadow)

    # Image→GImageに変換
    gimage_bg = GImage(box_size=BASE_SIZE)
    gimage_bg.paste(im=bg)

    return gimage_bg


def __create_weapon_img(weapon: status_model.Weapon, img_size: tuple[int, int]):
    """武器画像を生成します

    Args:
        weapon (status_model.Weapon): weaponオブジェクト
        img_size (tuple[int, int]): weapon画像のサイズ

    Returns:
        Image.Image: 武器画像
    """
    weapon_img = Image.open(weapon.util.icon.path).convert(
        "RGBA").resize((128, 128))
    weapon_paste = Image.new("RGBA", img_size, (255, 255, 255, 0))

    mask = weapon_img.copy()
    weapon_paste.paste(weapon_img, (1430, 50), mask=mask)

    return weapon_paste


def __gen_weapon_reality(weapon: status_model.Weapon):
    """武器のレアリティ画像を生成します

    Args:
        weapon (status_model.Weapon): weaponオブジェクト

    Returns:
        Image.Image: 武器レアリティ画像
    """
    img = Image.open(ASSETS.artifacter.reality[weapon.rank]).convert("RGBA")
    img = img.resize(
        (int(img.width*0.97), int(img.height*0.97))
    )
    paste = Image.new("RGBA", BASE_SIZE, (255, 255, 255, 0))
    mask = img.copy()

    paste.paste(img, (1422, 173), mask=mask)
    return paste

def __gen_weapon_status_icon(image_path:str, xy: tuple[int, int]):
    """武器のステータスのアイコン画像を生成します

    Args:
        weapon (status_model.Weapon): weaponオブジェクト

    Returns:
        Image.Image: 武器レアリティ画像
    """
    Base = Image.new("RGBA", BASE_SIZE, (255, 255, 255, 0))
    BaseAtk = Image.open(image_path).resize((23, 23))
    BaseAtkmask = BaseAtk.copy()
    Base.paste(BaseAtk, xy, mask=BaseAtkmask)
    return Base

def __gen_talent_img(talent_path: str):
    """単体の天賦アイコン画像を生成します

    Args:
        talent_path (str): 天賦画像のパス

    Returns:
        Image.Image: 単体の天賦アイコン画像
    """
    paste = Image.new("RGBA", TALENT_BASE_SIZE, (255, 255, 255, 0))
    talent = Image.open(talent_path).resize((50, 50)).convert('RGBA')
    mask = talent.copy()
    paste.paste(
        talent,
        (paste.width//2-25, paste.height//2-25,),
        mask=mask,
    )
    talent_obj = Image.alpha_composite(paste, TALENT_BASE)
    return talent_obj

def __gen_artifact_image(artifact: status_model.Artifact):
    """聖遺物の画像を生成します

    Args:
        artifact (status_model.Artifact): artifactオブジェクト

    Returns:
        Image.Image: 聖遺物の画像
    """
    PreviewPaste = Image.new('RGBA', BASE_SIZE, (255, 255, 255, 0))
    print(type(artifact))
    Preview = Image.open(artifact.util.icon.path).resize((256, 256))
    enhancer = ImageEnhance.Brightness(Preview)
    Preview = enhancer.enhance(0.6)
    Preview = Preview.resize(
        (int(Preview.width*1.3), int(Preview.height*1.3)))
    Pmask1 = Preview.copy()

    Pmask = Image.open(ASSETS.artifacter.mask.artifact_mask).convert('L').resize(Preview.size)
    Preview.putalpha(Pmask)
    if artifact.util.equip_type in ['flower', 'crown']:
        PreviewPaste.paste(Preview, (-37+373*0, 570), mask=Pmask1)
    elif artifact.util.equip_type in ['wing', 'cup']:
        PreviewPaste.paste(Preview, (-36+373*0, 570), mask=Pmask1)
    else:
        PreviewPaste.paste(Preview, (-35+373*0, 570), mask=Pmask1)
    Base = Image.new('RGBA', BASE_SIZE, (255, 255, 255, 0))
    Base = Image.alpha_composite(Base, PreviewPaste)
    return Base

def __gen_talent_list_img(character: status_model.Character):
    """単体の天賦アイコン画像をリスト状にした画像を生成します

    Args:
        character (status_model.Character): キャラクターデータ

    Returns:
        Image.Image: リスト状の天賦アイコン画像
    """
    paste = Image.new("RGBA", BASE_SIZE, (255, 255, 255, 0))
    with ThreadPoolExecutor(thread_name_prefix="talents") as executor:
        talents = [
            executor.submit(__gen_talent_img, v.util.icon.path) for v in
            character.skills
        ]
    for i, v in enumerate(talents):
        talent = v.result()
        paste.paste(talent, (15, 330+i*105))
    return paste


def __gen_constellation_img(constellation_icon_path: str, constellation_base: Image.Image):
    """単体の命の星座アイコン画像とベース画像を合成した画像を生成します

    Args:
        constellation_icon_path (str): 命の星座アイコン画像のパス
        constellation_base (Image.Image): 命の星座アイコンのベース画像

    Returns:
        Image.Image: 単体の命の星座画像
    """
    chara_constellation = Image.open(constellation_icon_path).convert(
        "RGBA").resize((45, 45))
    chara_constellation_paste = Image.new("RGBA", constellation_base.size, (255, 255, 255, 0))
    chara_constellation_mask = chara_constellation.copy()
    chara_constellation_paste.paste(chara_constellation, (int(chara_constellation_paste.width/2)-25,
                        int(chara_constellation_paste.height/2)-23), mask=chara_constellation_mask)
    constellation_object = Image.alpha_composite(constellation_base, chara_constellation_paste)
    return constellation_object


def __gen_constellation_list_img(character: status_model.Character):
    """リスト状の命の星座アイコン画像を生成します

    Args:
        character (status_model.Character): キャラクターデータ

    Returns:
        Image.Image: リスト状の星座画像
    """
    constellation_paste = Image.new("RGBA", BASE_SIZE, (255, 255, 255, 0))
    constellation_base, constellation_lock = CONSTELLATIONBACKS[character.util.element]
    clock_mask = constellation_lock.copy()
    with ThreadPoolExecutor(thread_name_prefix="constellations") as executor:
        constellation_objects = [
            executor.submit(__gen_constellation_img, v.path, constellation_base) for v in character.constellation_list
        ]
    for i in range(6):
        if len(constellation_objects) > i:
            constellation_paste.paste(constellation_objects[i], (666, 83+i*93))
        else:
            constellation_paste.paste(constellation_lock, (666, 83+i*93), mask=clock_mask)
    return constellation_paste


def __get_rounded_rectangle(xy: tuple[tuple[int, int], tuple[int, int]]):
    """なんかよく見る角丸の黒い背景画像を生成します

    Args:
        xy (tuple[tuple[int, int], tuple[int, int]]): 座標

    Returns:
        Image.Image: なんかよく見る角丸の黒い背景画像
    """
    # image以外のオブジェクト読み込んでるので変更したほうがいいかも・・・
    img = GImage(box_size=BASE_SIZE).get_image()
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(xy=xy,  radius=2, fill="black")
    return img

def __create_status_add(base: int, add: int, type: str, path: str) -> Image.Image:
    """キャラクターの個別のステータスの画像を取得します。これはHPなど合成数が利用されるもの専用です。

    Args:
        base (int): ベースの数値
        add (int): 装備の数値

    Returns:
        Image: キャラクターの個別のステータスの画像
    """

    img = GImage(
        box_size=(600, 100),
        default_font_size=22,
    )

    img.add_image(
        image_path=path,
        box=(50, 50),
        size=(45, 45),
        image_anchor=ImageAnchors.MIDDLE_MIDDLE
    )

    img.draw_text(
        text=type,
        position=(86, 50),
        anchor=Anchors.LEFT_MIDDLE,
    )
    # ベース値の合成
    img.draw_text(
        text=str(base),
        position=(302, 75),
        anchor=Anchors.LEFT_MIDDLE,
        font_size=18,
        font_color=Colors.GENSHIN_LIGHT_BLUE,
    )
    # 追加値の合成
    img.draw_text(
        text=f"+ {add}",
        position=(365, 75),
        anchor=Anchors.LEFT_MIDDLE,
        font_size=18,
        font_color=Colors.GENSHIN_GREEN,
    )
    # 合成値の合成
    img.draw_text(
        text=str(base + add),
        position=(300, 50),
        anchor=Anchors.LEFT_MIDDLE,
        font_size=26
    )

    return img.get_image()

def __create_status(status: Decimal, type: str, path: str, suffix="%") -> Image.Image:
    """キャラクターの個別のステータスの画像を取得します。suffixは％などの文字列です

    Args:
        status (int): ステータスの数値
        suffix (str): 後ろにつける文字. Defaults to "%".

    Returns:
        Image.Image: キャラクターの個別のステータス画像
    """
    img = GImage(
        box_size=(600, 100),
        default_font_size=26,
    )

    # ステータスのアイコン
    img.add_image(
        image_path=path,
        box=(50, 50),
        size=(40, 40),
        image_anchor=ImageAnchors.MIDDLE_MIDDLE
    )
    # ステータス名
    img.draw_text(
        text=type,
        position=(86, 50),
        anchor=Anchors.LEFT_MIDDLE,
    )
    # ステータスの合成
    img.draw_text(
        text=f"{status}{suffix}",
        position=(300, 50),
        anchor=Anchors.LEFT_MIDDLE,
        font_size=26
    )

    return img.get_image()

def __create_full_status(character: status_model.Character):
    """ステータス部分の画像を生成します

    Args:
        character (status_model.Character): キャラクターデータ

    Returns:
        Image.Image: ステータス部分の画像
    """
    img = GImage(
        box_size=BASE_SIZE,
        default_font_size=25,
    )
    futures: list[Future] = []
    with ThreadPoolExecutor(max_workers=20, thread_name_prefix="__create_status") as pool:
        # HP
        futures.append(
            pool.submit(
                __create_status_add,
                character.base_hp,
                character.added_hp,
                "HP",
                ASSETS.icon.status.hp
            )
        )
        # 攻撃
        futures.append(
            pool.submit(
                __create_status_add,
                character.base_attack,
                character.added_attack,
                "攻撃力",
                ASSETS.icon.status.attack
            )
        )
        # 防御
        futures.append(
            pool.submit(
                __create_status_add,
                character.base_defense,
                character.added_defense,
                "防御力",
                ASSETS.icon.status.diffence
            )
        )
        # 元素熟知
        futures.append(
            pool.submit(
                __create_status,
                character.elemental_mastery,
                "元素熟知",
                ASSETS.icon.status.element,
                ""
            )
        )
        # クリ率
        futures.append(
            pool.submit(
                __create_status,
                character.critical_rate,
                "会心率",
                ASSETS.icon.status.critical
            )
        )
        # クリダメ
        futures.append(
            pool.submit(
                __create_status,
                character.critical_damage,
                "会心ダメージ",
                ASSETS.icon.status.critical_per
            )
        )
        # 元チャ
        futures.append(
            pool.submit(
                __create_status,
                character.charge_efficiency,
                "元素チャージ効率",
                ASSETS.icon.status.element_charge,
            )
        )
        # 元素攻撃力
        if character.elemental_name is not None:
            futures.append(
                pool.submit(
                    __create_status,
                    character.elemental_value,
                    character.elemental_name,
                    ASSETS.icon.element[character.elemental_name],
                    ""
                )
            )

    for i, f in enumerate(futures):
        im: Image = f.result()
        # 各画像を合成します
        img.paste(im=im, box=(1360, 67+i*70))

    return img.get_image()

def __create_full_character_status(character: status_model.Character):
    """完全なキャラクターの画像を生成します

    Args:
        character (status_model.Character): キャラクターデータ

    Returns:
        Image.Image: 完全なキャラクターの画像
    """
    base = GImage(
        box_size=BASE_SIZE,
        default_font_size=25,
    )
    print("一応うごいてんぞ")
    base.draw_text(position=(30, 20), text=character.util.name, font_size=48)
    chara_lv = f"Lv.{character.level:>2}"
    love = str(character.love)
    chara_lv_length = base.get_textsize(chara_lv)[0]
    love_length = base.get_textsize(love)[0]
    base.draw_text(position=(30, 20), text=chara_lv)
    base.paste(
        __get_rounded_rectangle(xy=(
            (40 + chara_lv_length, 74),
            (77 + chara_lv_length + love_length, 102)
        ))
    )
    base.add_image(
        box=(42+chara_lv_length, 76),
        image_path=ASSETS.artifacter.love,
        size=(25, 25)
    )
    base.draw_text(position=(73+chara_lv_length, 74), text=love)
    for i, skill in enumerate(character.skills):
        base.draw_text(
            position=(42, 397 + (i * 105)),
            text=f"Lv.{skill.level}",
            font_size=17,
            font_color=Colors.GENSHIN_LIGHT_BLUE if skill.level >= 10 else Colors.WHITE
        )

    base.paste(
        __create_full_status(
            character=character
        )
    )

    return base.get_image()

def __create_weapon(weapon: status_model.Weapon) -> Image.Image:
    """武器画像を生成します

    Args:
        weapon (weapon): weaponオブジェクト

    Returns:
        Image.Image: 武器画像
    """
    img = GImage(
        box_size=BASE_SIZE,
        default_font_size=45,
    )
    # 武器画像を合成
    img.paste(
        __create_weapon_img(weapon=weapon, img_size=(128, 128))
    )
    # 武器レアリティの合成
    img.paste(
        __gen_weapon_reality(weapon=weapon)
    )
    # 武器名の合成
    img.draw_text_with_max_width(
        text=weapon.util.name,
        max_width=400,
        position=(1582, 47),
        font_size=24,
        anchor=Anchors.RIGHT_BOTTOM,
    )
    # 武器のステータスの合成
    img.draw_text(
        text=f'基礎攻撃力  {weapon.main_value}',
        position=(1623, 120),
        font_size=23,
        anchor=Anchors.RIGHT_BOTTOM,
    )
    with ThreadPoolExecutor(max_workers=20, thread_name_prefix="__create_weapon_icon") as pool:
        weapon_icon = pool.submit(
            __gen_weapon_status_icon,
            ASSETS.icon.status.attack,
            (1600, 155)
        )
    img.paste(
        weapon_icon
    )
    if weapon.sub_value is not None:
        img.draw_text(
            text=f'{weapon.sub_jp_name}  {weapon.sub_value}',
            position=(1623, 155),
            font_size=23,
            anchor=Anchors.RIGHT_BOTTOM,
        )
        with ThreadPoolExecutor(max_workers=20, thread_name_prefix="__create_weapon_icon") as pool:
            weapon_icon = pool.submit(
                __gen_weapon_status_icon,
                ASSETS.icon_namehash[weapon.sub_name],
                (1600, 155)
            )
        img.paste(
            weapon_icon
        )
    # 武器のレベル情報の合成
    img.paste(
        __get_rounded_rectangle(xy=(
            (1582, 80),
            (1582 + img.get_textsize(str(weapon.level))[0], 108)
        ))
    )
    img.draw_text(
        text=f'R{weapon.level}',
        position=(1584, 82), 
        font_size=24, 
        anchor=Anchors.RIGHT_BOTTOM)
    # 武器の凸情報の合成
    img.paste(
        __get_rounded_rectangle(xy=(
            (1430, 45),
            (1470, 70)
        ))
    )
    img.draw_text(
        text=f'R{weapon.rank}',
        position=(1433, 46), 
        font_size=24, 
        anchor=Anchors.RIGHT_BOTTOM)

    return img.get_image()

def __create_artifact(artifact: status_model.Artifact) -> Image.Image:
    """個別の聖遺物の画像を生成します。

    Args:
        artifact (artifact): アーティファクトオブジェクト

    Returns:
        Image.Image: アーティファクトの画像
    """
    base_img = GImage(
        box_size=(360, 415),
        default_font_size=18
    )
    if artifact is None:
        return base_img.get_image()

    # 聖遺物の画像を合成
    base_img.paste(
        im=__gen_artifact_image(artifact=artifact),    
    )
    # 聖遺物の画像を合成
    base_img.add_image(
        image_path=artifact.util.icon.path,
        size=(66, 70),
        box=(70, 70),
        image_anchor=ImageAnchors.MIDDLE_MIDDLE
    )
    # メインオプション名
    base_img.draw_text(
        text=artifact.main_jp_name, 
        position=(375, 655), 
        anchor=Anchors.MIDDLE_BOTTOM, 
        font_size=29)
    # メインオプションアイコン
    base_img.add_image(
        ASSETS.icon_namehash[artifact.main_name],
        (340+0*373-int(base_img.get_textsize(artifact.main_jp_name, 29)[0]), 655),
    )
    # 聖遺物のメインのステータスを合成
    base_img.draw_text(
        text=artifact.main_value_str + artifact.suffix,
        position=(375+0*373, 690),
        font_size=49,
        anchor=Anchors.RIGHT_DESCENDER
    )
    # 聖遺物レベル
    levlen = base_img.get_textsize(f'+{artifact.level}', 21)[0]
    base_img.paste(
        __get_rounded_rectangle(((373+0*373-int(levlen), 748), (375+0*373, 771)))
    )
    base_img.draw_text(
        text=f'+{artifact.level}', 
        position=(374+0*373-levlen, 749), 
        font_size=21)
    
    # 聖遺物のサブステータスを合成
    for i, v in enumerate(artifact.status):
        # 色分け処理
        if v.jp_name in ['HP', '攻撃力', '防御力']:
            base_img.draw_text(
                position=(79+373*0, 811+50*i),
                text=v.jp_name,
                font_size=25,
                font_color=(255, 255, 255, 190),
                anchor=Anchors.RIGHT_BOTTOM
            )
            base_img.draw_text(text=v.value_str, position=(375, 811+50*i), font_size=25, font_color=(255, 255, 255, 190))
        else:
            base_img.draw_text(
                position=(79+373*0, 811+50*i),
                text=v.jp_name,
                font_size=25,
                anchor=Anchors.RIGHT_BOTTOM
            )
            base_img.draw_text(text=v.value_str, position=(375, 811+50*i), font_size=25)
        substatus_icon = GImage(image_path=ASSETS.icon_namehash[v.name])
        base_img.paste(im=substatus_icon, box=(44, 811+50*i))

    base_img.draw_text(text=artifact.score, position=(380, 1016), font_size=36, anchor=Anchors.RIGHT_BOTTOM)
    base_img.draw_text(text='Score', position=(295, 1025), font_size=27, font_color=(160, 160, 160, 0))

    for grade in [0, 1, 2]:
        if artifact.score >= ARTIFACTER_REFER[artifact.util.equip_type][grade]:
            ScoreImage = GImage(image_path=ASSETS.artifacter.artifact_grades[3-grade])
            break
    else:
        ScoreImage = GImage(image_path=ASSETS.artifacter.artifact_grades[0])

    base_img.paste(ScoreImage, (85, 1013))

    return base_img.get_image()

def __create_total_socre(artifact_list: dict[str, status_model.Artifact], build_type: str) -> Image.Image:
    """聖遺物のトータルスコアの画像を生成します

    Args:
        artifact_list (list[artifact]): 聖遺物の配列
        element_color (tuple[int, int, int]): 元素属性のカラー

    Returns:
        Image.Image: 聖遺物のトータルスコア画像
    """
    total_score = round(sum([v.score for v in artifact_list.values()]), 1)
    img = GImage(box_size=BASE_SIZE, default_font_size=40)
    # スコア合計
    img.draw_text(
        position=(1652, 420), 
        text=str(total_score), 
        font_size=75,
        anchor=Anchors.MIDDLE_BOTTOM
    )
    # スコア計算方法
    img.draw_text(
        position=(1867, 585), 
        text=f'{build_type}換算', 
        font_size=24,
        anchor=Anchors.RIGHT_BOTTOM
    )

    if total_score >= 220:
        ScoreEv = Image.open(ASSETS.artifacter.artifact_grades[3])
    elif total_score >= 200:
        ScoreEv = Image.open(ASSETS.artifacter.artifact_grades[2])
    elif total_score >= 180:
        ScoreEv = Image.open(ASSETS.artifacter.artifact_grades[1])
    else:
        ScoreEv = Image.open(ASSETS.artifacter.artifact_grades[0])

    ScoreEv = ScoreEv.resize((ScoreEv.width//8, ScoreEv.height//8))
    EvMask = ScoreEv.copy()

    # 本家ではこのペースト時にEvMaskでマスクしてる。GImageにマスクないねん。
    img.paste(im=ScoreEv, box=(1806, 345))

    return img

def __create_artifact_list(artifact_map: dict[status_model.Artifact]) -> Image.Image:
    """聖遺物の一覧の画像を生成します。

    Args:
        artifact_list (list[artifact]): アーティファクトオブジェクトの配列
        element_color (tuple[int, int, int]): 元素属性のカラー

    Returns:
        Image.Image: 聖遺物一覧画像
    """
    print("create_artifact_list起動")
    img = GImage(
        box_size=BASE_SIZE,
    )

    futures: list[Future] = []
    # 各聖遺物のステータス画像の生成
    with ThreadPoolExecutor(max_workers=20, thread_name_prefix="__create_artifact") as pool:
        for i, v in enumerate(['EQUIP_BRACER', 'EQUIP_NECKLACE', 'EQUIP_SHOES', 'EQUIP_RING', 'EQUIP_DRESS']):
            futures.append(
                pool.submit(
                    __create_artifact,
                    artifact_map[v]
                )
            )
    # 各ステータス画像の合成
    for i, v in enumerate(futures):
        im: Image = v.result()
        img.paste(im=im, box=(375*i, 1025))

    return img.get_image()

def __create_image(character: status_model.Character) -> Image.Image:
    """キャラデータから画像を生成します。

    Args:
        char_data (CharacterStatus): キャラデータ

    Returns:
        Image.Image: キャラ画像
    """
    print("create_image起動")
    artifacts = character.artifacts
    weapon = character.weapon

    with ThreadPoolExecutor(thread_name_prefix="__create") as pool:
        # 背景画像の取得
        bgf: Future = pool.submit(
            __create_background,
            character,
        )

        # スターとレベル、凸の画像を取得
        lvf: Future = pool.submit(
            __create_full_character_status, character)

        # 天賦を取得
        skillf: Future = pool.submit(
            __gen_talent_list_img,
            character,
        )

        # 聖遺物画像の取得
        artifactf: Future = pool.submit(
            __create_artifact_list,
            artifacts,
        )

        # 聖遺物のトータルスコアを取得
        total_scoref: Future = pool.submit(
            __create_total_socre,
            artifacts,
            character.build_type,
        )

        weapon_dataf: Future = pool.submit(
            __create_weapon,
            weapon,
        )

    # 各リザルトを取得
    bg = bgf.result()
    lv = lvf.result()
    skill = skillf.result()
    artifact = artifactf.result()
    total_score = total_scoref.result()
    weapon_data = weapon_dataf.result()

    # レベルなど合成
    bg.paste(im=lv, image_anchor=ImageAnchors.LEFT_BOTTOM)
    # 天賦を合成
    bg.paste(im=skill)
    # 聖遺物を合成
    bg.paste(
        im=artifact,
        image_anchor=ImageAnchors.RIGHT_TOP
    )
    # 聖遺物のトータルスコアを合成
    bg.paste(im=total_score)
    # 武器画像を合成
    bg.paste(
        im=weapon_data,
        image_anchor=ImageAnchors.LEFT_BOTTOM
    )
    return bg.get_image()

def save_image(file_path: str, character_status: status_model.Character):
    if cache_image.check_cache_exists(file_path=file_path):
        return

    character_status.init_utils()
    character_status.init_score()
    image = __create_image(character=character_status)
    image = image.convert("RGB")
    image.save(file_path, optimize=True, quality=100)
    cache_image.cache_append(file_path=file_path)

