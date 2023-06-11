from io import BytesIO
from lib.gen_image import GImage, Colors, Algin, Anchors, ImageAnchors
from concurrent.futures import ThreadPoolExecutor, Future
import model.status_model as status_model
import model.util_model as util_model
from PIL import Image, ImageFilter, ImageDraw
from repository.assets_repository import ASSETS
from decimal import Decimal
import lib.cache_image as cache_image


def __create_background(element: str, gacha_icon: str, position: util_model.Position) -> GImage:
    """キャラ画像を合成したバックグラウンドを生成します。

    Args:
        element (str): 属性の名前
        charaname (str): キャラの名前

    Returns:
        GImage: 合成した画像
    """
    # 元素別の画像
    img = GImage(
        image_path=ASSETS.genshin_status.backgroundo_elements[element],
        default_font_size=26,
    )

    img.add_image(
        image_path=ASSETS.genshin_status.background_shadow,
    )
    x, y = img.get_image().size
    x //= 2
    y //= 2
    # キャラ画像
    img.add_image(
        box=(position.x+x, position.y+y),
        scale=position.scale,
        image_path=gacha_icon,
        image_anchor=ImageAnchors.MIDDLE_MIDDLE
    )
    # オーバーレイ画像
    img.add_image(image_path=ASSETS.genshin_status.background_base)

    return img


def __create_star_and_lv(quantity: int, lv: int, constellations: str) -> Image.Image:
    """★とレベル、凸のイメージを作成します

    Args:
        quantity (int): ★の個数
        lv (int): レベル
        totu (str): 凸

    Returns:
        Image: 合成した画像
    """
    totu = [
        "無", "1", "2", "3", "4", "5", "完"
    ]

    img = GImage(
        box_size=(500, 30),
        default_font_size=26,
    )
    # ★の合成
    for i in range(quantity):
        img.add_image(
            image_path=ASSETS.genshin_status.star,
            box=(i*35, 2),
        )
    # レベルと凸
    img.draw_text(
        text=f'Lv {lv}  {totu[constellations]}凸',
        position=(380, 2),
        align=Algin.RIGHT,
        anchor=Anchors.RIGHT_TOP
    )

    return img.get_image()


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
        size=(55, 55),
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
        default_font_size=22,
    )

    img.add_image(
        image_path=path,
        box=(50, 50),
        size=(55, 55),
        image_anchor=ImageAnchors.MIDDLE_MIDDLE
    )

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


def __create_full_status(
    hp_base: int,
    hp_add: int,
    atk_base: int,
    atk_add: int,
    df_base: int,
    df_add: int,
    mas: int,
    cri: Decimal,
    cri_dmg: Decimal,
    mas_chg: Decimal,
    elmt: str = None,
    elmt_dmg: int = None,
    element_icon: str = None,
) -> Image.Image:
    """すべてのステータスのデータを取得します。

    Args:
        hp_base (int): ベースHP
        hp_add (int): 装備HP
        atk_base (int): ベース攻撃
        atk_add (int): 装備攻撃
        df_base (int): ベース防御
        df_add (int): 装備防御
        mas (int): 元素熟知
        cri (float): 会心率
        cri_dmg (float): 会心ダメージ率
        mas_chg (float): 元素チャージ
        elmt (str, optional): 元素タイプ. Defaults to None.
        elmt_dmg (int, optional): 元素倍率. Defaults to None.

    Returns:
        Image.Image: ステータスの画像
    """

    img = GImage(
        box_size=(600, 1000),
        default_font_size=24,
    )
    futures: list[Future] = []
    with ThreadPoolExecutor(max_workers=20, thread_name_prefix="__create_status") as pool:
        # HP
        futures.append(
            pool.submit(
                __create_status_add,
                hp_base,
                hp_add,
                "HP",
                ASSETS.icon.status.hp
            )
        )
        # 攻撃
        futures.append(
            pool.submit(
                __create_status_add,
                atk_base,
                atk_add,
                "攻撃力",
                ASSETS.icon.status.attack
            )
        )
        # 防御
        futures.append(
            pool.submit(
                __create_status_add,
                df_base,
                df_add,
                "防御力",
                ASSETS.icon.status.diffence
            )
        )
        # 元素熟知
        futures.append(
            pool.submit(
                __create_status,
                mas,
                "元素熟知",
                ASSETS.icon.status.element,
                ""
            )
        )
        # クリ率
        futures.append(
            pool.submit(
                __create_status,
                cri,
                "会心率",
                ASSETS.icon.status.critical
            )
        )
        # クリダメ
        futures.append(
            pool.submit(
                __create_status,
                cri_dmg,
                "会心ダメージ",
                ASSETS.icon.status.critical_per
            )
        )
        # 元チャ
        futures.append(
            pool.submit(
                __create_status,
                mas_chg,
                "元素チャージ効率",
                ASSETS.icon.status.element_charge,
            )
        )
        # 元素攻撃力
        if elmt is not None:
            futures.append(
                pool.submit(
                    __create_status,
                    elmt_dmg,
                    elmt,
                    element_icon,
                    ""
                )
            )

    height = 480//len(futures)
    for i, f in enumerate(futures):
        im: Image = f.result()
        # 各画像を合成します
        img.paste(im=im, box=(0, height*i))

    return img.get_image()


def __create_skill(skill_icon: str, skill_name: str, skill_lv: str, element_color: tuple[int, int, int]) -> Image.Image:
    """個別のスキルの画像を生成します

    Args:
        skill_icon (str): スキルのアイコンurl
        skill_lv (str): スキルレベルの文字列
        charaname (str): キャラクター名
        skill_name (str): スキルの名称
        element_color (tuple[int, int, int]): 元素属性のカラー

    Returns:
        Image.Image: スキル画像
    """
    img = GImage(
        box_size=(320, 100),
        default_font_size=48,
    )
    # スキルの画像を合成
    img.add_image(image_path=skill_icon, box=(60, 50), size=(
        100, 100), image_anchor=ImageAnchors.MIDDLE_MIDDLE)
    # スキルレベルの合成
    img.draw_text(
        text="Lv",
        position=(165, 0),
        anchor=Anchors.LEFT_ASCENDER
    )
    img.draw_text(
        text=skill_lv,
        position=(300, 0),
        anchor=Anchors.RIGHT_ASCENDER
    )
    skill_type_base = Image.new(
        mode="RGBA",
        size=(120, 28),
        color=element_color,
    )
    name_position = (235, 80)

    img.paste(im=skill_type_base, box=name_position,
              image_anchor=ImageAnchors.MIDDLE_MIDDLE)
    img.draw_text(
        text=skill_name,
        position=name_position,
        anchor=Anchors.MIDDLE_MIDDLE,
        align=Algin.CENTER,
        font_size=18
    )
    return img.get_image()


def __create_skill_list(skills: list[status_model.Skill], element_color: tuple[int, int, int]) -> Image.Image:
    """すべての天賦スキルをまとめた画像を生成します

    Args:
        character (character): キャラクターオブジェクト
        element_color (tuple[int, int, int]): 元素属性のカラー

    Returns:
        Image.Image: スキルをまとめた画像
    """

    img = GImage(
        box_size=(600, 1000),
    )
    futures: list[Future] = []
    with ThreadPoolExecutor(max_workers=20, thread_name_prefix="__create_skill") as pool:
        # 各スキル画像の生成
        for i, skill in enumerate(skills):
            futures.append(
                pool.submit(
                    __create_skill,
                    skill.util.icon.path,
                    skill.util.name,
                    skill.level + skill.add_level,
                    element_color
                )
            )
    # スキル画像の合成
    for i, v in enumerate(futures):
        im: Image = v.result()
        img.paste(im=im, box=(0, 135*i))

    return img.get_image()


def __create_artifact(artifact: status_model.Artifact, angle: int, element_color: tuple[int, int, int]) -> Image.Image:
    """個別の聖遺物の画像を生成します。

    Args:
        artifact (artifact): アーティファクトオブジェクト
        element_color (tuple[int, int, int]): 元素属性のカラー

    Returns:
        Image.Image: アーティファクトの画像
    """
    base_img = GImage(
        box_size=(580, 140),
        default_font_size=18
    )
    if artifact is None:
        return base_img.get_image()

    # 聖遺物の背景を合成
    base_img.add_rotate_image(
        image_path=ASSETS.genshin_status.artufact_bg[artifact.star],
        box=(66, 70),
        size=(220, 220),
        angle=angle,
    )
    # 聖遺物の画像を合成
    base_img.add_image(
        image_path=artifact.util.icon.path,
        size=(66, 70),
        box=(70, 70),
        image_anchor=ImageAnchors.MIDDLE_MIDDLE
    )
    img = GImage(
        box_size=(560, 100),
        default_font_size=16
    )
    artifact_main_name_size = 20
    main_name = artifact.main_jp_name
    if len(main_name) >= 7:
        artifact_main_name_size = 15
    # 聖遺物のメインステータス名を合成
    img.draw_text(
        text=main_name,
        position=(124, 30),
        font_size=artifact_main_name_size,
        anchor=Anchors.RIGHT_DESCENDER
    )
    # 聖遺物のメインのステータスを合成
    img.draw_text(
        text=artifact.main_value_str,
        position=(124, 70),
        font_size=30,
        anchor=Anchors.RIGHT_DESCENDER
    )
    # 聖遺物のサブステータスを合成
    for i, v in enumerate(artifact.status):
        img.draw_text(
            text=v.jp_name,
            position=(140+155*(i//2), 30*(i % 2)),
            anchor=Anchors.LEFT_ASCENDER
        )
        img.draw_text(
            text=v.value_str,
            position=(230+155*(i//2), 30*(i % 2)),
            anchor=Anchors.LEFT_ASCENDER
        )
    # 聖遺物スコアなどの背景合成
    bg = Image.new(mode="RGBA", size=(187, 30), color=element_color)

    img.paste(bg, box=(200, 80), image_anchor=ImageAnchors.LEFT_MIDDLE)
    # 聖遺物のスコアを合成
    img.draw_text(
        text="スコア",
        position=(280, 80),
        anchor=Anchors.LEFT_MIDDLE
    )
    img.draw_text(
        text=str(round(artifact.score, 1)),
        position=(372, 80),
        anchor=Anchors.RIGHT_MIDDLE
    )
    # 聖遺物のレベルを合成
    img.draw_text(
        text=f"+{artifact.level}",
        position=(248, 80),
        anchor=Anchors.RIGHT_MIDDLE
    )
    base_img.paste(im=img, box=(120, 20))
    return base_img.get_image()


def __create_artifact_list(artifact_map: dict[status_model.Artifact], element_color: tuple[int, int, int]) -> Image.Image:
    """聖遺物の一覧の画像を生成します。

    Args:
        artifact_list (list[artifact]): アーティファクトオブジェクトの配列
        element_color (tuple[int, int, int]): 元素属性のカラー

    Returns:
        Image.Image: 聖遺物一覧画像
    """
    img = GImage(
        box_size=(600, 720),
    )

    futures: list[Future] = []
    # 各聖遺物のステータス画像の生成
    with ThreadPoolExecutor(max_workers=20, thread_name_prefix="__create_artifact") as pool:
        for i, v in enumerate(['EQUIP_BRACER', 'EQUIP_NECKLACE', 'EQUIP_SHOES', 'EQUIP_RING', 'EQUIP_DRESS']):
            futures.append(
                pool.submit(
                    __create_artifact,
                    artifact_map.get(v),
                    144*i,
                    element_color,
                )
            )
    # 各ステータス画像の合成
    for i, v in enumerate(futures):
        im: Image = v.result()
        img.paste(im=im, box=(0, 120*i))

    return img.get_image()


def __create_total_socre(artifact_list: dict[str, status_model.Artifact], element_color: tuple[int, int, int, int], build_type: str) -> Image.Image:
    """聖遺物のトータルスコアの画像を生成します

    Args:
        artifact_list (list[artifact]): 聖遺物の配列
        element_color (tuple[int, int, int]): 元素属性のカラー

    Returns:
        Image.Image: 聖遺物のトータルスコア画像
    """
    total_score = round(sum([v.score for v in artifact_list.values()]), 1)
    mask = Image.new(mode="L", size=(600, 50), color=0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle(((30, 12), (570, 38)), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(6))
    bg = Image.new(mode="RGBA", size=(600, 50), color=(0, 0, 0, 255))
    bg.putalpha(mask)
    color_bg = Image.new(
        mode="RGBA",
        color=element_color,
        size=(540, 28)
    )
    img = GImage(box_size=(600, 80), default_font_size=40)
    img.paste(bg, box=(0, 30))
    img.paste(color_bg, box=(30, 40))
    img.draw_text(
        text=f"計算方式: {build_type}  スコア合計:",
        position=(420, 40),
        anchor=Anchors.RIGHT_MIDDLE,
        font_size=25
    )
    img.draw_text(
        text=str(total_score),
        position=(550, 35),
        anchor=Anchors.RIGHT_MIDDLE
    )
    return img


def __create_weapon(weapon: status_model.Weapon, element_color: tuple[int, int, int]) -> Image.Image:
    """武器画像を生成します

    Args:
        weapon (weapon): weaponオブジェクト
        element_color (tuple[int, int, int]): 元素属性のカラー

    Returns:
        Image.Image: 武器画像
    """
    img = GImage(
        box_size=(600, 300),
        default_font_size=45,
    )
    # 武器画像を合成
    img.add_image(
        image_path=weapon.util.icon.path,
        size=(160, 160),
        box=(0, 250),
        image_anchor=ImageAnchors.LEFT_BOTTOM
    )
    # 武器名の合成
    img.draw_text(
        text=weapon.util.name,
        position=(570, 160),
        anchor=Anchors.RIGHT_BOTTOM,
    )
    # 武器のステータスの合成
    if weapon.sub_value is not None:
        weapon_status = f"{weapon.main_jp_name} {weapon.main_value} / {weapon.sub_jp_name} {weapon.sub_value}"
    else:
        weapon_status = f"{weapon.main_jp_name} {weapon.main_value}"
    img.draw_text(
        text=weapon_status,
        position=(570, 200),
        anchor=Anchors.RIGHT_BOTTOM,
        font_size=20
    )
    # 凸情報などの背景を作成し合成
    bg = Image.new(mode="RGBA", size=(220, 30), color=element_color)
    img.paste(im=bg, box=(570, 255), image_anchor=ImageAnchors.RIGHT_BOTTOM)
    # 凸情報などのテキストを合成
    img.draw_text(
        text=f"武器ランク{weapon.rank}  Lv {weapon.level}",
        position=(550, 255), anchor=Anchors.RIGHT_DESCENDER,
        font_size=20
    )

    return img.get_image()


def __create_image(character: status_model.Character) -> Image.Image:
    """キャラデータから画像を生成します。

    Args:
        char_data (CharacterStatus): キャラデータ

    Returns:
        Image.Image: キャラ画像
    """
    ELEMENT_COLOR: dict[str, tuple[int, int, int]] = {
        "Electric": (144, 89, 181),
        "Fire": (209, 89, 73),
        "Grass": (75, 150, 52),
        "Ice": (60, 145, 187),
        "Rock": (167, 120, 26),
        "Water": (53, 89, 166),
        "Wind": (84, 157, 118)
    }

    artifacts = character.artifacts
    weapon = character.weapon
    element_color = ELEMENT_COLOR[character.util.element]

    with ThreadPoolExecutor(thread_name_prefix="__create") as pool:
        # 背景画像の取得
        bgf: Future = pool.submit(
            __create_background,
            character.util.element,
            character.costume.gacha_icon.path,
            character.costume.position,
        )

        # スターとレベル、凸の画像を取得
        lvf: Future = pool.submit(
            __create_star_and_lv, character.star, character.level, character.constellations)

        # ステータスを取得
        statusf: Future = pool.submit(
            __create_full_status,
            character.base_hp,
            character.added_hp,
            character.base_attack,
            character.added_attack,
            character.base_defense,
            character.added_defense,
            character.elemental_mastery,
            character.critical_rate,
            character.critical_damage,
            character.charge_efficiency,
            character.elemental_jp_name,
            character.elemental_value,
            ASSETS.icon.element[character.elemental_name]
        )

        # 天賦を取得
        skillf: Future = pool.submit(
            __create_skill_list,
            character.skills,
            element_color
        )

        # 聖遺物画像の取得
        artifactf: Future = pool.submit(
            __create_artifact_list,
            artifacts,
            element_color
        )

        # 聖遺物のトータルスコアを取得
        total_scoref: Future = pool.submit(
            __create_total_socre,
            artifacts,
            element_color,
            character.build_name
        )

        weapon_dataf: Future = pool.submit(
            __create_weapon,
            weapon,
            element_color
        )

    # 各リザルトを取得
    bg = bgf.result()
    lv = lvf.result()
    status = statusf.result()
    skill = skillf.result()
    artifact = artifactf.result()
    total_score = total_scoref.result()
    weapon_data = weapon_dataf.result()

    # ステータスを合成
    bg.paste(im=status, box=(12, 15))
    # レベルなど合成
    bg.paste(im=lv, box=(40, 687), image_anchor=ImageAnchors.LEFT_BOTTOM)
    # 天賦を合成
    bg.paste(im=skill, box=(1005, 45))
    # 聖遺物を合成
    bg.paste(
        im=artifact,
        box=(1920, 100),
        image_anchor=ImageAnchors.RIGHT_TOP
    )
    # 聖遺物のトータルスコアを合成
    bg.paste(im=total_score, box=(1320, 27))
    # 武器画像を合成
    bg.paste(
        im=weapon_data,
        box=(720, 732),
        image_anchor=ImageAnchors.LEFT_BOTTOM
    )
    # キャラ名を合成
    bg.draw_text(
        text=character.util.name,
        font_size=86,
        position=(38, 642),
        anchor=Anchors.LEFT_DESCENDER
    )

    return bg.get_image()


def get_character_image_bytes(character_status: status_model.Character) -> bytes:
    """キャラクターステータスのオブジェクトからDiscord FileとPathを生成します。

    Args:
        character_status (CharacterStatus): キャラクター情報の入ったオブジェクト

    Returns:
        bytes: Discord FileとPathの入ったTuple型
    """

    image = __create_image(character_status)
    image.show()
    fileio = BytesIO()
    image = image.convert("RGB")
    image.save(fileio, format="JPEG", optimize=True, quality=100)
    return fileio.getvalue()


def save_image(file_path: str, character_status: status_model.Character):
    if cache_image.check_cache_exists(file_path=file_path):
        return

    character_status.init_utils()
    character_status.init_score()
    image = __create_image(character=character_status)
    image = image.convert("RGB")
    image.save(file_path, optimize=True, quality=100)
    cache_image.cache_append(file_path=file_path)
