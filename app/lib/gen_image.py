from PIL import Image, ImageFont, ImageDraw
from typing import TypeVar, Union
import os


class Colors:
    """色の列挙型のようなものです
    """
    RED = (0xff, 0x00, 0x00, 0xff)
    GREEN = (0x00, 0xff, 0x00, 0xff)
    BLUE = (0x00, 0x00, 0xff, 0x7f)
    YELLOW = (0xff, 0xff, 0x00, 0xff)
    CYAN = (0xff, 0x00, 0xff, 0xff)
    MAGENTA = (0x00, 0xff, 0xff, 0xff)
    WHITE = (0xff, 0xff, 0xff, 0xff)
    CLEAR = (0xff, 0xff, 0xff, 0x00)
    CLEAR_RED = (0xff, 0x00, 0x00, 0x7f)
    GENSHIN_LIGHT_BLUE = (118, 255, 255, 0xff)
    GENSHIN_GREEN = (169, 255, 0, 0xff)


class Anchors:
    """アンカーの列挙型のようなものです
    """
    RIGHT_ASCENDER = "ra"
    RIGHT_TOP = "rt"
    RIGHT_MIDDLE = "rm"
    RIGHT_BASELINE = "rs"
    RIGHT_BOTTOM = "rm"
    RIGHT_DESCENDER = "rd"
    LEFT_ASCENDER = "la"
    LEFT_TOP = "lt"
    LEFT_MIDDLE = "lm"
    LEFT_BASELINE = "ls"
    LEFT_BOTTOM = "lm"
    LEFT_DESCENDER = "ld"
    MIDDLE_ASCENDER = "ma"
    MIDDLE_TOP = "mt"
    MIDDLE_MIDDLE = "mm"
    MIDDLE_BASELINE = "ms"
    MIDDLE_BOTTOM = "mm"
    MIDDLE_DESCENDER = "md"


class ImageAnchors:
    """イメージ用のアンカーの列挙型のようなものです
    """
    RIGHT_TOP = (1, 0)
    RIGHT_MIDDLE = (1, 0.5)
    RIGHT_BOTTOM = (1, 1)
    LEFT_TOP = (0, 0)
    LEFT_MIDDLE = (0, 0.5)
    LEFT_BOTTOM = (0, 1)
    MIDDLE_TOP = (0.5, 0)
    MIDDLE_MIDDLE = (0.5, 0.5)
    MIDDLE_BOTTOM = (1, 0.5)


class Algin:
    """左右中央揃えの列挙型のようなものです
    """
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


TypeGImage = TypeVar("TypeGImage", bound="GImage",)


def _open_image(path: str, raise_exception: bool = False):
    if os.path.exists(path):
        return Image.open(path)
    elif raise_exception:
        raise FileNotFoundError(path)
    else:
        # pathが存在しない場合はデフォルトの場合は1pxの透明画像を返却します
        return Image.new(mode="RGBA", size=[100, 100], color=Colors.CLEAR)


class GImage:
    """Pillowを利用した画像を生成するラッパークラスです。自身をベースに他のGImageオブジェクトを合成するなどの操作が可能です。
    """

    def __init__(
        self,
        image_path: str = None,
        box_size: tuple[int, int] = None,
        default_font_path: str = "./font/ja-jp.ttf",
        default_font_size: int = 30,
        default_font_color: Colors = Colors.WHITE,
    ) -> None:
        """コンストラクタです。image_pathもしくはbox_sizeを指定してイメージを作成します。

        Args:
            image_path (str, optional): 画像のpath. Defaults to None.
            box_size (tuple[int, int], optional): 空の画像のサイズ. Defaults to None.
            default_font_path (str, optional): デフォルトのフォントパス. Defaults to "uzura.ttf".
            default_font_size (int, optional): デフォルトのフォントサイズ. Defaults to 30.
            default_font_color (Colors, optional): デフォルトのフォントカラー. Defaults to Colors.WHITE.

        Raises:
            ValueError: image_path と boxの値が正しくない場合にraiseします
        """
        # raiseの種類たぶんカバレッジおいきれてないので他のエラー出たら気にしとく事
        if image_path is not None:
            self.__image = _open_image(image_path).convert('RGBA').copy()
        elif len(box_size) == 2:
            self.__image = Image.new(
                mode="RGBA", size=box_size, color=Colors.CLEAR)
        else:
            raise ValueError(
                "Either image path or box size, one value must be valid")
        self.set_default_font_color(default_font_color)
        self.set_default_font_size(default_font_size)
        self.set_font_path(default_font_path)

    def set_default_font_size(self, font_size: int) -> None:
        """デフォルトのフォントサイズを指定します。

        Args:
            font_size (int): フォントサイズ
        """
        self.default_font_size = font_size

    def set_default_font_color(self, font_color: tuple[int, int, int, int]) -> None:
        """デフォルトのフォントカラーを指定します。これはRGBAもしくはRGBをTupleで指定します。

        Args:
            font_color (tuple[int,int,int,int]): フォントカラー
        """
        self.default_font_color = font_color

    def set_font_path(self, font_path: str):
        """フォントのPathを指定します。

        Args:
            font_path (str): フォントのPath
        """
        self.font_path = font_path

    def __get_font(self, font_path: str = None, font_size: int = None) -> ImageFont.FreeTypeFont:
        """フォントオブジェクトを取得します。
        引数に指定がない場合はデフォルトで指定されたフォントが使用されます。
        これは内部的のみ使用します。

        Args:
            font_path (str, optional): フォントパス. Defaults to None.
            font_size (int, optional): フォントサイズ. Defaults to None.

        Returns:
            ImageFont.FreeTypeFont: フォントオブジェクト
        """

        if font_size is None:
            font_size = self.default_font_size
        if font_path is None:
            font_path = self.font_path
        return ImageFont.truetype(font=font_path, size=font_size)

    def get_image(self):
        """Pillowのイメージオブジェクトを返します

        Returns:
            Image.Image: Imageオブジェクト
        """
        return self.__image

    def draw_text(
        self,
        text: str,
        position: tuple[int, int],
        anchor: str = None,
        align: str = None,
        font_size: int = None,
        font_color: tuple[int, int, int, int] = None,
        font_path: str = None,
    ) -> None:
        """現在の画像にテキストを描画します。フォントサイズ、フォントカラー、フォントパスは省略された場合デフォルトが利用されます。

        Args:
            text (str): 描画するテキスト
            position (tuple[int, int]): 描画位置
            anchor (str): 基準点
            align (str): テキストの左右中央そろえ
            font_size (int, optional): フォントサイズ. Defaults to None.
            font_color (Colors, optional): フォントカラー. Defaults to None.
            font_path (str, optional): フォントパス. Defaults to None.
        """
        draw = ImageDraw.Draw(im=self.__image)
        draw.text(
            xy=position,
            text=str(text),
            fill=font_color,
            font=self.__get_font(font_path=font_path, font_size=font_size),
            anchor=anchor,
            align=align,
        )

    def draw_text_with_max_width(
        self,
        text: str,
        position: tuple[int, int],
        max_width: int,
        anchor: str = None,
        align: str = None,
        font_size: int = None,
        font_color: tuple[int, int, int, int] = None,
        font_path: str = None,
    ):
        draw = ImageDraw.Draw(im=self.__image)
        font = self.__get_font(font_path=font_path, font_size=font_size)
        font_size = font.size

        textsize = draw.textsize(text=text, font=font)

        if max_width < textsize[0]:
            font_size = int(font_size * max_width / textsize[0])

        draw.text(
            xy=position,
            text=str(text),
            fill=font_color,
            font=self.__get_font(font_path=font_path, font_size=font_size),
            anchor=anchor,
            align=align,
        )

    def get_textsize(
        self,
        text: str,
        font_size: int = None,
        font_path: str = None,
    ):
        draw = ImageDraw.Draw(im=self.__image)
        font = self.__get_font(font_path=font_path, font_size=font_size)
        return draw.textsize(text=text, font=font)

    def paste(
        self,
        im: Union[Image.Image, TypeGImage],
        box: tuple[int, int] = (0, 0),
        image_anchor: tuple[int, int] = ImageAnchors.LEFT_TOP
    ) -> None:
        """PillowのImageオブジェクト又はGImageオブジェクトを合成できます

        Args:
            im (Union[Image.Image, GImage]): イメージオブジェクト
            box (tuple[int, int], optional): 描画位置. Defaults to (0, 0).
            image_anchor (tuple[int, int], optional): 基準点. Defaults to ImageAnchors.LEFT_TOP.

        Raises:
            ValueError: imに自身のオブジェクトを指定するとエラー
        """

        if self == im:
            raise ValueError(
                "Because the same object is specified, PASTE cannot be performed.")
        if not isinstance(im, Image.Image):
            im = im.get_image()

        box = (
            box[0] - int(im.size[0]*image_anchor[0]),
            box[1] - int(im.size[1]*image_anchor[1])
        )
        self.__image.alpha_composite(im=im, dest=box)

    def add_image(
        self,
        image_path: str,
        box: tuple[int, int] = (0, 0),
        size: tuple[int, int] = None,
        scale: int = None,
        image_anchor: tuple[int, int] = ImageAnchors.LEFT_TOP
    ) -> None:
        """現在の画像にpngファイルなどの画像を読み込んで合成します。

        Args:
            image_path (str): 画像のPath
            box (tuple[int, int], optional): 描画位置. Defaults to (0, 0).
            size (tuple[int, int], optional): 画像サイズ（縦横比を固定しているため、はみ出る部分の上限として考えてください）. Defaults to None.
            image_anchor (tuple[int, int], optional): 基準点. Defaults to ImageAnchors.LEFT_TOP.
        """
        im = _open_image(image_path).convert('RGBA')
        if size is not None:
            x = size[0]
            y = size[1]
            aspect_ratio = im.size[0] / im.size[1]
            resize_ratio = x / y
            if aspect_ratio > resize_ratio:
                x = int(y*aspect_ratio)
            else:
                y = int(x*aspect_ratio)
            im = im.resize(size=size)
        elif scale is not None:

            x = im.size[0] * scale // 100
            y = im.size[1] * scale // 100
            im = im.resize(size=(x, y))

        box = (
            box[0] - int(im.size[0]*image_anchor[0]),
            box[1] - int(im.size[1]*image_anchor[1])
        )
        self.__image.alpha_composite(im=im, dest=box)

    def add_rotate_image(
        self,
        image_path: str,
        box: tuple[int, int] = (0, 0),
        size: tuple[int, int] = None,
        image_anchor: tuple[int, int] = ImageAnchors.MIDDLE_MIDDLE,
        angle: int = 0,
    ) -> None:
        """現在の画像にpngファイルなどの画像を読み込んで合成します。

        Args:
            image_path (str): 画像のPath
            box (tuple[int, int], optional): 描画位置. Defaults to (0, 0).
            size (tuple[int, int], optional): 画像サイズ（縦横比を固定しているため、はみ出る部分の上限として考えてください）. Defaults to None.
            image_anchor (tuple[int, int], optional): 基準点. Defaults to ImageAnchors.LEFT_TOP.
        """
        im = _open_image(image_path).convert('RGBA')
        if size is not None:
            im.thumbnail(size=size)
        bg = Image.new(mode="RGBA", size=(
            im.size[0]*2, im.size[1]*2), color=Colors.CLEAR)
        diff = (im.size[0]//2, im.size[1]//2)
        bg.alpha_composite(im=im, dest=diff)
        bg = bg.rotate(angle=angle, resample=Image.BICUBIC)
        box = (
            box[0] - int(im.size[0]*image_anchor[0])-diff[0],
            box[1] - int(im.size[1]*image_anchor[1])-diff[1]
        )
        self.__image.alpha_composite(im=bg, dest=box)

    def show(self):
        """デバッグ用、出来上がった画像を表示します。
        """
        self.__image.show()

    def save(self, image_path):
        """指定のファイルに画像を保存します。
        """
        self.__image.save(fp=image_path)
