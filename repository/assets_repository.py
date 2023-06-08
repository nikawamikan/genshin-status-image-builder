import model.assets_model as assets
import pathlib


def static_init():
    global ASSETS

    BASE_PATH = pathlib.Path("image/assets")
    BACKGROUND = BASE_PATH / "background"
    ARTIFACT = BASE_PATH / "artifactbg"
    ICON = BASE_PATH / "icons"
    ICON_ELEMENT = ICON / "element"
    ICON_STATUS = ICON / "status"

    ASSETS = assets.Assets(
        background_base=str(BACKGROUND / "base.png"),
        background_shadow=str(BACKGROUND/ "shadow.png"),
        backgroundo_elements={
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
        icon=assets.Icon(
            element={
                "Electric": str(ICON_ELEMENT / "Electric.png"),
                "Fire": str(ICON_ELEMENT / "Fire.png"),
                "Grass": str(ICON_ELEMENT / "Grass.png"),
                "Ice": str(ICON_ELEMENT / "Ice.png"),
                "Rock": str(ICON_ELEMENT / "Rock.png"),
                "Water": str(ICON_ELEMENT / "Water.png"),
                "Wind": str(ICON_ELEMENT / "Wind.png"),
                "Physics": str(ICON_STATUS / "attack.png"),
                None: "",  # ダミー
            },
            status=assets.Status(
                attack=str(ICON_STATUS / "attack.png"),
                element_charge=str(ICON_STATUS / "charge.png"),
                critical=str(ICON_STATUS / "crtc.png"),
                critical_per=str(ICON_STATUS / "crtcper.png"),
                diffence=str(ICON_STATUS / "diffence.png"),
                element=str(ICON_STATUS / "element.png"),
                hp=str(ICON_STATUS / "hp.png"),
            )
        ),
        star=str(BASE_PATH / "ster.png")
    )


static_init()
