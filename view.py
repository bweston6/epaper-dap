from PIL import Image, ImageDraw, ImageFont
from menu import ListMenu, TileMenu, MenuItem
from pathlib import Path


class View:
    def __init__(self, display):
        self.display = display
        self.bitmaps_dir = (Path(__file__).parent / "./assets/bitmaps").resolve()
        self.fonts_dir = (Path(__file__).parent / "./assets/fonts").resolve()

    def render_listmenu(self, menu):
        FIRST_ITEM_BASELINE = 41
        REGULAR_FONT_SIZE = 15
        SMALL_FONT_SIZE = 11
        LINE_HEIGHT = 16

        font_regular = ImageFont.truetype(
            (self.fonts_dir / "Cantarell-VF.otf").resolve(), size=REGULAR_FONT_SIZE
        )
        font_small = ImageFont.truetype(
            (self.fonts_dir / "Cantarell-VF.otf").resolve(), size=SMALL_FONT_SIZE
        )
        bitmap = Image.open((self.bitmaps_dir / menu.background_bitmap).resolve())
        bitmap = bitmap.rotate(-90, expand=True)
        # modify bitmap in-place
        drawing = ImageDraw.Draw(bitmap)

        for i, child in enumerate(menu.children):
            drawing.text(
                (2, FIRST_ITEM_BASELINE + LINE_HEIGHT * i),
                child.name,
                font=font_regular,
                anchor="ls",
            )
            if isinstance(child, MenuItem):
                drawing.text(
                    (193, FIRST_ITEM_BASELINE + LINE_HEIGHT * i),
                    child.value,
                    font=font_small,
                    anchor="rs",
                )

        listmenu_buttons_bitmap = Image.open(
            (self.bitmaps_dir / "listmenu_buttons.bmp").resolve()
        )
        bitmap = bitmap.rotate(90, expand=True)
        bitmap.paste(listmenu_buttons_bitmap)
        self.display.displayPartBaseImage(self.display.getbuffer(bitmap))

    def render_tilemenu(self, menu):
        bitmap = Image.open((self.bitmaps_dir / menu.background_bitmap).resolve())
        self.display.displayPartBaseImage(self.display.getbuffer(bitmap))

    def render_menu(self, menu):
        self.display.init(self.display.FULL_UPDATE)
        if isinstance(menu, ListMenu):
            self.render_listmenu(menu)
        if isinstance(menu, TileMenu):
            self.render_tilemenu(menu)
        self.display.sleep()
