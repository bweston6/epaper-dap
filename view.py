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
        FIRST_ITEM_START = 28
        LINE_HEIGHT = 16
        LINE_WIDTH = 92
        MAX_DISPLAY_ITEMS = 6
        REGULAR_FONT_SIZE = 15
        SMALL_FONT_SIZE = 11
        BLACK = 0
        WHITE = 1

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

        start_child_index = max(
            0,
            menu.children.index(menu.selected_child) - MAX_DISPLAY_ITEMS - 1,
        )
        end_child_index = start_child_index + MAX_DISPLAY_ITEMS

        for i, child in enumerate(menu.children[start_child_index:end_child_index]):
            font_color = BLACK

            # invert background for selected items
            if child is menu.selected_child:
                font_color = WHITE
                drawing.rectangle(
                    [
                        (0, FIRST_ITEM_START + LINE_HEIGHT * i),
                        (LINE_WIDTH, FIRST_ITEM_START + LINE_HEIGHT * (i + 1)),
                    ],
                    not font_color,
                )

            # draw name
            drawing.text(
                (2, FIRST_ITEM_BASELINE + LINE_HEIGHT * i),
                child.name,
                fill=font_color,
                font=font_regular,
                anchor="ls",
            )

            # draw value for MenuItems
            if isinstance(child, MenuItem):
                drawing.text(
                    (193, FIRST_ITEM_BASELINE + LINE_HEIGHT * i),
                    child.value,
                    fill=font_color,
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
