from PIL import Image, ImageFont, ImageDraw, ImageEnhance, ImageFilter
import os
from collections import Counter
import model.status_model as status_model
from concurrent.futures import ThreadPoolExecutor
from lib.gen_image import GImage
from repository.assets_repository import ASSETS

cwd = os.path.abspath(os.path.dirname(__file__))

BASE_SIZE = (1920, 1080)
TALENT_BASE_SIZE = (int(149/1.5), int(137/1.5))
TALENT_BACK = Image.open()
TALENT_BASE = Image.open(ASSETS.artifacter.talent_back).resize(TALENT_BASE_SIZE)

CONSTELLATIONBACKS = {
    k: (
        Image.open(v.unlock).resize((90, 90)).convert('RGBA'),
        Image.open(v.lock).resize((90, 90)).convert('RGBA'),
    ) for k, v in ASSETS.artifacter.constellations.items()
}


def config_font(size):
    return ImageFont.truetype(f'{cwd}/Assets/ja-jp.ttf', size)


def __gen_base_img(character: status_model.Character):
    bg = GImage(ASSETS.artifacter.background[character.util.element]).get_image()
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

    return bg


def __gen_weapon_img(weapon: status_model.Weapon, img_size: tuple(int, int)):
    weapon_img = Image.open(weapon.util.icon.path).convert("RGBA").resize((128, 128))
    weapon_paste = Image.new("RGBA", img_size, (255, 255, 255, 0))

    mask = weapon_img.copy()
    weapon_paste.paste(weapon_img, (1430, 50), mask=mask)

    return weapon_paste


def __gen_weapon_reality(weapon: status_model.Weapon):
    img = Image.open(ASSETS.artifacter.reality[weapon.rank]).convert("RGBA")
    img = img.resize(
        (int(img.width*0.97), int(img.height*0.97))
    )
    paste = Image.new("RGBA", BASE_SIZE, (255, 255, 255, 0))
    mask = img.copy()

    paste.paste(img, (1422, 173), mask=mask)
    return paste


def __gen_talent_img(talent_path: str):
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


def __gen_talent_list_img(character: status_model.Character):
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


def __gen_constellation_img(constellation_icon_path: str, c_base: Image.Image):
    chara_c = Image.open(constellation_icon_path).convert("RGBA").resize((45, 45))
    chara_c_paste = Image.new("RGBA", c_base.size, (255, 255, 255, 0))
    chara_c_mask = chara_c.copy()
    chara_c_paste.paste(chara_c, (int(chara_c_paste.width/2)-25,
                        int(chara_c_paste.height/2)-23), mask=chara_c_mask)
    c_object = Image.alpha_composite(c_base, chara_c_paste)
    return c_object


def __gen_constellation_list_img(character: status_model.Character):
    c_paste = Image.new("RGBA", BASE_SIZE, (255, 255, 255, 0))
    c_base, c_lock = CONSTELLATIONBACKS[character.util.element]
    clock_mask = c_lock.copy()
    with ThreadPoolExecutor(thread_name_prefix="constellations") as executor:
        c_objects = [
            executor.submit(__gen_constellation_img, v.path, c_base) for v in character.constellation_list
        ]
    for i in range(6):
        if len(c_objects) > i:
            c_paste.paste(c_objects[i], (666, 83+i*93))
        else:
            c_paste.paste(c_lock, (666, 83+i*93), mask=clock_mask)



def generation(data):
    

    D = ImageDraw.Draw(Base)

    D.text((30, 20), CharacterName, font=config_font(48))
    levellength = D.textlength("Lv."+str(CharacterLevel), font=config_font(25))
    friendshiplength = D.textlength(str(FriendShip), font=config_font(25))
    D.text((35, 75), "Lv."+str(CharacterLevel), font=config_font(25))
    D.rounded_rectangle((35+levellength+5, 74, 77+levellength +
                        friendshiplength, 102), radius=2, fill="black")
    FriendShipIcon = Image.open(f'{cwd}/Assets/Love.png').convert("RGBA")
    FriendShipIcon = FriendShipIcon.resize(
        (int(FriendShipIcon.width*(24/FriendShipIcon.height)), 24))
    Fmask = FriendShipIcon.copy()
    Base.paste(FriendShipIcon, (42+int(levellength), 76), mask=Fmask)
    D.text((73+levellength, 74), str(FriendShip), font=config_font(25))

    D.text((42, 397), f'Lv.{CharacterTalent["通常"]}', font=config_font(
        17), fill='aqua' if CharacterTalent["通常"] >= 10 else None)
    D.text((42, 502), f'Lv.{CharacterTalent["スキル"]}', font=config_font(
        17), fill='aqua' if CharacterTalent["スキル"] >= 10 else None)
    D.text((42, 607), f'Lv.{CharacterTalent["爆発"]}', font=config_font(
        17), fill='aqua' if CharacterTalent["爆発"] >= 10 else None)

    def genbasetext(state):
        sumv = CharacterStatus[state]
        plusv = sumv - CharacterBase[state]
        basev = CharacterBase[state]
        return f"+{format(plusv,',')}", f"{format(basev,',')}", D.textlength(f"+{format(plusv,',')}", font=config_font(12)), D.textlength(f"{format(basev,',')}", font=config_font(12))

    disper = ['会心率', '会心ダメージ', '攻撃パーセンテージ', '防御パーセンテージ', 'HPパーセンテージ', '水元素ダメージ', '物理ダメージ', '風元素ダメージ',
              '岩元素ダメージ', '炎元素ダメージ', '与える治癒効果', '与える治療効果', '雷元素ダメージ', '氷元素ダメージ', '草元素ダメージ', '与える治癒効果', '元素チャージ効率']
    StateOP = ('HP', '攻撃力', "防御力", "元素熟知", "会心率", "会心ダメージ", "元素チャージ効率")
    for k, v in CharacterStatus.items():
        if k in ['氷元素ダメージ', '水元素ダメージ', '岩元素ダメージ', '草元素ダメージ', '風元素ダメージ', '炎元素ダメージ', '物理ダメージ', '与える治癒効果', '雷元素ダメージ'] and v == 0:
            k = f'{element}元素ダメージ'
        try:
            i = StateOP.index(k)
        except:
            i = 7
            D.text((844, 67+i*70), k, font=config_font(26))
            opicon = Image.open(f'{cwd}/emotes/{k}.png').resize((40, 40))
            oppaste = Image.new('RGBA', BASE_SIZE, (255, 255, 255, 0))
            opmask = opicon.copy()
            oppaste.paste(opicon, (789, 65+i*70))
            Base = Image.alpha_composite(Base, oppaste)
            D = ImageDraw.Draw(Base)

        if k not in disper:
            statelen = D.textlength(format(v, ","), config_font(26))
            D.text((1360-statelen, 67+i*70),
                   format(v, ","), font=config_font(26))
        else:
            statelen = D.textlength(f'{float(v)}%', config_font(26))
            D.text((1360-statelen, 67+i*70),
                   f'{float(v)}%', font=config_font(26))

        if k in ['HP', '防御力', '攻撃力']:
            HPpls, HPbase, HPsize, HPbsize = genbasetext(k)
            D.text((1360-HPsize, 97+i*70), HPpls,
                   fill=(0, 255, 0, 180), font=config_font(12))
            D.text((1360-HPsize-HPbsize-1, 97+i*70), HPbase,
                   font=config_font(12), fill=(255, 255, 255, 180))

    D.text((1582, 47), WeaponName, font=config_font(26))
    wlebellen = D.textlength(f'Lv.{WeaponLevel}', font=config_font(24))
    D.rounded_rectangle((1582, 80, 1582+wlebellen+4, 108),
                        radius=1, fill='black')
    D.text((1584, 82), f'Lv.{WeaponLevel}', font=config_font(24))

    BaseAtk = Image.open(f'{cwd}/emotes/基礎攻撃力.png').resize((23, 23))
    BaseAtkmask = BaseAtk.copy()
    Base.paste(BaseAtk, (1600, 120), mask=BaseAtkmask)
    D.text((1623, 120), f'基礎攻撃力  {WeaponBaseATK}', font=config_font(23))

    optionmap = {
        "攻撃パーセンテージ": "攻撃%",
        "防御パーセンテージ": "防御%",
        "元素チャージ効率": "元チャ効率",
        "HPパーセンテージ": "HP%",
    }
    if WeaponSubOPKey != None:
        BaseAtk = Image.open(
            f'{cwd}/emotes/{WeaponSubOPKey}.png').resize((23, 23))
        BaseAtkmask = BaseAtk.copy()
        Base.paste(BaseAtk, (1600, 155), mask=BaseAtkmask)

        D.text((1623, 155), f'{optionmap.get(WeaponSubOPKey) or WeaponSubOPKey}  {str(WeaponSubOPValue)+"%" if WeaponSubOPKey in disper else format(WeaponSubOPValue,",")}', font=config_font(23))

    D.rounded_rectangle((1430, 45, 1470, 70), radius=1, fill='black')
    D.text((1433, 46), f'R{WeaponRank}', font=config_font(24))

    ScoreLen = D.textlength(f'{ScoreTotal}', config_font(75))
    D.text((1652-ScoreLen//2, 420), str(ScoreTotal), font=config_font(75))
    blen = D.textlength(f'{ScoreCVBasis}換算', font=config_font(24))
    D.text((1867-blen, 585), f'{ScoreCVBasis}換算', font=config_font(24))

    if ScoreTotal >= 220:
        ScoreEv = Image.open(f'{cwd}/artifactGrades/SS.png')
    elif ScoreTotal >= 200:
        ScoreEv = Image.open(f'{cwd}/artifactGrades/S.png')
    elif ScoreTotal >= 180:
        ScoreEv = Image.open(f'{cwd}/artifactGrades/A.png')
    else:
        ScoreEv = Image.open(f'{cwd}/artifactGrades/B.png')

    ScoreEv = ScoreEv.resize((ScoreEv.width//8, ScoreEv.height//8))
    EvMask = ScoreEv.copy()

    Base.paste(ScoreEv, (1806, 345), mask=EvMask)

    # 聖遺物
    atftype = list()
    for i, parts in enumerate(['flower', "wing", "clock", "cup", "crown"]):
        details = ArtifactsData.get(parts)

        if not details:
            continue
        atftype.append(details['type'])
        PreviewPaste = Image.new('RGBA', BASE_SIZE, (255, 255, 255, 0))
        Preview = Image.open(
            f'{cwd}/Artifact/{details["type"]}/{parts}.png').resize((256, 256))
        enhancer = ImageEnhance.Brightness(Preview)
        Preview = enhancer.enhance(0.6)
        Preview = Preview.resize(
            (int(Preview.width*1.3), int(Preview.height*1.3)))
        Pmask1 = Preview.copy()

        Pmask = Image.open(
            f'{cwd}/Assets/ArtifactMask.png').convert('L').resize(Preview.size)
        Preview.putalpha(Pmask)
        if parts in ['flower', 'crown']:
            PreviewPaste.paste(Preview, (-37+373*i, 570), mask=Pmask1)
        elif parts in ['wing', 'cup']:
            PreviewPaste.paste(Preview, (-36+373*i, 570), mask=Pmask1)
        else:
            PreviewPaste.paste(Preview, (-35+373*i, 570), mask=Pmask1)
        Base = Image.alpha_composite(Base, PreviewPaste)
        D = ImageDraw.Draw(Base)

        mainop = details['main']['option']

        mainoplen = D.textlength(optionmap.get(
            mainop) or mainop, font=config_font(29))
        D.text((375+i*373-int(mainoplen), 655),
               optionmap.get(mainop) or mainop, font=config_font(29))
        MainIcon = Image.open(
            f'{cwd}/emotes/{mainop}.png').convert("RGBA").resize((35, 35))
        MainMask = MainIcon.copy()
        Base.paste(MainIcon, (340+i*373-int(mainoplen), 655), mask=MainMask)

        mainv = details['main']['value']
        if mainop in disper:
            mainvsize = D.textlength(f'{float(mainv)}%', config_font(49))
            D.text((375+i*373-mainvsize, 690),
                   f'{float(mainv)}%', font=config_font(49))
        else:
            mainvsize = D.textlength(format(mainv, ","), config_font(49))
            D.text((375+i*373-mainvsize, 690),
                   format(mainv, ","), font=config_font(49))
        levlen = D.textlength(f'+{details["Level"]}', config_font(21))
        D.rounded_rectangle((373+i*373-int(levlen), 748,
                            375+i*373, 771), fill='black', radius=2)
        D.text((374+i*373-levlen, 749),
               f'+{details["Level"]}', font=config_font(21))

        if details['Level'] == 20 and details['rarelity'] == 5:
            c_data = {}
            for a in details["sub"]:
                if a['option'] in disper:
                    c_data[a['option']] = str(float(a["value"]))
                else:
                    c_data[a['option']] = str(a["value"])
            psb = culculate_op(c_data)

        if len(details['sub']) == 0:
            continue

        for a, sub in enumerate(details['sub']):
            SubOP = sub['option']
            SubVal = sub['value']
            if SubOP in ['HP', '攻撃力', '防御力']:
                D.text((79+373*i, 811+50*a), optionmap.get(SubOP) or SubOP,
                       font=config_font(25), fill=(255, 255, 255, 190))
            else:
                D.text((79+373*i, 811+50*a), optionmap.get(SubOP)
                       or SubOP, font=config_font(25))
            SubIcon = Image.open(f'{cwd}/emotes/{SubOP}.png').resize((30, 30))
            SubMask = SubIcon.copy()
            Base.paste(SubIcon, (44+373*i, 811+50*a), mask=SubMask)
            if SubOP in disper:
                SubSize = D.textlength(f'{float(SubVal)}%', config_font(25))
                D.text((375+i*373-SubSize, 811+50*a),
                       f'{float(SubVal)}%', font=config_font(25))
            else:
                SubSize = D.textlength(format(SubVal, ","), config_font(25))
                if SubOP in ['防御力', '攻撃力', 'HP']:
                    D.text((375+i*373-SubSize, 811+50*a), format(SubVal, ","),
                           font=config_font(25), fill=(255, 255, 255, 190))
                else:
                    D.text((375+i*373-SubSize, 811+50*a), format(SubVal,
                           ","), font=config_font(25), fill=(255, 255, 255))

            if details['Level'] == 20 and details['rarelity'] == 5:
                nobi = D.textlength(
                    "+".join(map(str, psb[a])), font=config_font(11))
                D.text((375+i*373-nobi, 840+50*a), "+".join(map(str,
                       psb[a])), fill=(255, 255, 255, 160), font=config_font(11))

        Score = float(ScoreData[parts])
        ATFScorelen = D.textlength(str(Score), config_font(36))
        D.text((380+i*373-ATFScorelen, 1016), str(Score), font=config_font(36))
        D.text((295+i*373-ATFScorelen, 1025), 'Score',
               font=config_font(27), fill=(160, 160, 160))

        PointRefer = {
            "total": {
                "SS": 220,
                "S": 200,
                "A": 180
            },
            "flower": {
                "SS": 50,
                "S": 45,
                "A": 40
            },
            "wing": {
                "SS": 50,
                "S": 45,
                "A": 40
            },
            "clock": {
                "SS": 45,
                "S": 40,
                "A": 35
            },
            "cup": {
                "SS": 45,
                "S": 40,
                "A": 37
            },
            "crown": {
                "SS": 40,
                "S": 35,
                "A": 30
            }
        }

        if Score >= PointRefer[parts]['SS']:
            ScoreImage = Image.open(f'{cwd}/artifactGrades/SS.png')
        elif Score >= PointRefer[parts]['S']:
            ScoreImage = Image.open(f'{cwd}/artifactGrades/S.png')
        elif Score >= PointRefer[parts]['A']:
            ScoreImage = Image.open(f'{cwd}/artifactGrades/A.png')
        else:
            ScoreImage = Image.open(f'{cwd}/artifactGrades/B.png')

        ScoreImage = ScoreImage.resize(
            (ScoreImage.width//11, ScoreImage.height//11))
        SCMask = ScoreImage.copy()

        Base.paste(ScoreImage, (85+373*i, 1013), mask=SCMask)

    SetBounus = Counter([x for x in atftype if atftype.count(x) >= 2])
    for i, (n, q) in enumerate(SetBounus.items()):
        if len(SetBounus) == 2:
            D.text((1536, 243+i*35), n, fill=(0, 255, 0), font=config_font(23))
            D.rounded_rectangle((1818, 243+i*35, 1862, 266+i*35), 1, 'black')
            D.text((1835, 243+i*35), str(q), font=config_font(19))
        if len(SetBounus) == 1:
            D.text((1536, 263), n, fill=(0, 255, 0), font=config_font(23))
            D.rounded_rectangle((1818, 263, 1862, 288), 1, 'black')
            D.text((1831, 265), str(q), font=config_font(19))

    Base.show()
    Base.save(f'{cwd}/Tests/Image.png')

    return pil_to_base64(Base, format='png')


def pil_to_base64(img, format="jpeg"):
    buffer = BytesIO()
    img.save(buffer, format)
    img_str = base64.b64encode(buffer.getvalue()).decode("ascii")

    return img_str


generation(read_json('data.json'))
