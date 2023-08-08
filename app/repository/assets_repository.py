import model.assets_model as assets
import pathlib


def static_init():
    global ASSETS

    BASE_PATH = pathlib.Path("image/assets")

    GENSHIN_STAT = BASE_PATH / "genshin_status_assets"
    BACKGROUND = GENSHIN_STAT / "background"
    ARTIFACT = GENSHIN_STAT / "artifactbg"

    ARTIFACTER = BASE_PATH / "artifacter_assets"
    GRADES = ARTIFACTER / "artifact_grades"
    ART_BG = ARTIFACTER / "background"
    CONSTELLATION = ARTIFACTER / "constellations"
    MASK = ARTIFACTER / "mask"
    RARLITY = ARTIFACTER / "Rarlity"

    ICON = BASE_PATH / "icons"
    ICON_ELEMENT = ICON / "element"
    ICON_STATUS = ICON / "status"

    PROFILE = BASE_PATH / "profile_assets"

    ASSETS = assets.Assets(
        # 原神すてーぼ用のディレクトリ
        genshin_status=assets.GenshinStatusAssets(
            background_base=str(BACKGROUND / "base.png"),
            background_shadow=str(BACKGROUND / "shadow.png"),
            background_elements={
                "Electric": str(BACKGROUND / "Electric.png"),
                "Fire": str(BACKGROUND / "Fire.png"),
                "Grass": str(BACKGROUND / "Grass.png"),
                "Ice": str(BACKGROUND / "Ice.png"),
                "Rock": str(BACKGROUND / "Rock.png"),
                "Water": str(BACKGROUND / "Water.png"),
                "Wind": str(BACKGROUND / "Wind.png"),
            },
            artufact_bg=[
                "",  # ダミー
                str(ARTIFACT / "1.png"),
                str(ARTIFACT / "2.png"),
                str(ARTIFACT / "3.png"),
                str(ARTIFACT / "4.png"),
                str(ARTIFACT / "5.png"),
            ],
            star=str(GENSHIN_STAT / "ster.png"),
        ),
        # Artifacter 用の画像ディレクトリ
        artifacter=assets.ArtifacterAssets(
            artifact_grades=[
                str(GRADES / "B.png"),
                str(GRADES / "A.png"),
                str(GRADES / "S.png"),
                str(GRADES / "SS.png"),
            ],
            background={
                "Electric": str(ART_BG / "Electric.png"),
                "Fire": str(ART_BG / "Fire.png"),
                "Grass": str(ART_BG / "Grass.png"),
                "Ice": str(ART_BG / "Ice.png"),
                "Rock": str(ART_BG / "Rock.png"),
                "Water": str(ART_BG / "Water.png"),
                "Wind": str(ART_BG / "Wind.png"),
            },
            mask=assets.ArtifacterMask(
                alhaithem=str(MASK / "Alhaitham.png"),
                artifact_mask=str(MASK / "ArtifactMask.png"),
                character_mask=str(MASK / "CharacterMask.png")
            ),
            reality=[
                "",
                str(RARLITY / "1.png"),
                str(RARLITY / "2.png"),
                str(RARLITY / "3.png"),
                str(RARLITY / "4.png"),
                str(RARLITY / "5.png"),
            ],
            love=str(ARTIFACTER / "Love.png"),
            shadow=str(ARTIFACTER / "Shadow.png"),
            talent_back=str(ARTIFACTER/"TalentBack.png"),
            constellations={
                "Electric": assets.Constellation(
                    lock=str(CONSTELLATION / "Electric.png"),
                    unlock=str(CONSTELLATION / "ElectricLock.png")
                ),
                "Fire": assets.Constellation(
                    lock=str(CONSTELLATION / "Fire.png"),
                    unlock=str(CONSTELLATION / "FireLock.png")
                ),
                "Grass": assets.Constellation(
                    lock=str(CONSTELLATION / "Grass.png"),
                    unlock=str(CONSTELLATION / "GrassLock.png")
                ),
                "Ice": assets.Constellation(
                    lock=str(CONSTELLATION / "Ice.png"),
                    unlock=str(CONSTELLATION / "IceLock.png")
                ),
                "Rock": assets.Constellation(
                    lock=str(CONSTELLATION / "Rock.png"),
                    unlock=str(CONSTELLATION / "RockLock.png")
                ),
                "Water": assets.Constellation(
                    lock=str(CONSTELLATION / "Water.png"),
                    unlock=str(CONSTELLATION / "WaterLock.png")
                ),
                "Wind": assets.Constellation(
                    lock=str(CONSTELLATION / "Wind.png"),
                    unlock=str(CONSTELLATION / "WindLock.png")
                ),
            }
        ),
        # Profile 用の画像ディレクトリ
        profile=assets.ProfileAssets(
            layer=str(PROFILE / "Layer.png")
        ),
        # 以下共有部
        icon=assets.Icon(
            element={
                "Electric": str(ICON_ELEMENT / "Electric.png"),
                "Fire": str(ICON_ELEMENT / "Fire.png"),
                "Grass": str(ICON_ELEMENT / "Grass.png"),
                "Ice": str(ICON_ELEMENT / "Ice.png"),
                "Rock": str(ICON_ELEMENT / "Rock.png"),
                "Water": str(ICON_ELEMENT / "Water.png"),
                "Wind": str(ICON_ELEMENT / "Wind.png"),
                "Physics": str(ICON_ELEMENT / "Physics.png"),
                None: "",  # ダミー
            },
            status=assets.Status(
                attack=str(ICON_STATUS / "attack.png"),
                element_charge=str(ICON_STATUS / "element_charge.png"),
                critical=str(ICON_STATUS / "crtc_dmg.png"),
                critical_per=str(ICON_STATUS / "crtc_per.png"),
                diffence=str(ICON_STATUS / "def.png"),
                element=str(ICON_STATUS / "element.png"),
                hp=str(ICON_STATUS / "HP.png"),
            )
        ),
        icon_namehash={
            "FIGHT_PROP_HP": str(ICON_STATUS / "HP.png"),
            "FIGHT_PROP_HP_PERCENT": str(ICON_STATUS / "hp_per.png"),
            "FIGHT_PROP_ATTACK": str(ICON_STATUS / "attack.png"),
            "FIGHT_PROP_ATTACK_PERCENT": str(ICON_STATUS / "attack_per.png"),
            "FIGHT_PROP_DEFENSE": str(ICON_STATUS / "def.png"),
            "FIGHT_PROP_DEFENSE_PERCENT": str(ICON_STATUS / "def_per.png"),
            "FIGHT_PROP_CRITICAL": str(ICON_STATUS / "crtc_dmg.png"),
            "FIGHT_PROP_CRITICAL_HURT": str(ICON_STATUS / "crtc_per.png"),
            "FIGHT_PROP_CHARGE_EFFICIENCY": str(ICON_STATUS / "element_charge.png"),
            "FIGHT_PROP_HEAL_ADD": str(ICON_STATUS / "treatment_given.png"),
            "FIGHT_PROP_HEALED_ADD": str(ICON_STATUS / "treatment_received.png"),
            "FIGHT_PROP_ELEMENT_MASTERY": str(ICON_STATUS / "element.png"),
            "FIGHT_PROP_PHYSICAL_ADD_HURT": str(ICON_ELEMENT / "Physics.png"),
            "FIGHT_PROP_FIRE_ADD_HURT": str(ICON_ELEMENT / "Fire.png"),
            "FIGHT_PROP_ELEC_ADD_HURT": str(ICON_ELEMENT / "Electric.png"),
            "FIGHT_PROP_WATER_ADD_HURT": str(ICON_ELEMENT / "Water.png"),
            "FIGHT_PROP_GRASS_ADD_HURT": str(ICON_ELEMENT / "Grass.png"),
            "FIGHT_PROP_WIND_ADD_HURT": str(ICON_ELEMENT / "Wind.png"),
            "FIGHT_PROP_ROCK_ADD_HURT": str(ICON_ELEMENT / "Rock.png"),
            "FIGHT_PROP_ICE_ADD_HURT": str(ICON_ELEMENT / "Ice.png"),
        },
    )


static_init()
