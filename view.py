from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from display import Display
from menu import ListMenu, TileMenu, MenuItem


class View:
    def __init__(self):
        self.display = Display(rotate=90)
        self.bitmaps_dir = (Path(__file__).parent /
                            "./assets/bitmaps").resolve()
        self.fonts_dir = (Path(__file__).parent / "./assets/fonts").resolve()

    def render_listmenu(self, menu, partial_refresh=False):
        FIRST_ITEM_BASELINE = 41
        FIRST_ITEM_START = 28
        LINE_HEIGHT = 16
        LINE_WIDTH = 198
        MAX_DISPLAY_ITEMS = 6
        REGULAR_FONT_SIZE = 15
        SMALL_FONT_SIZE = 11
        BLACK = 0
        WHITE = 255

        font_regular = ImageFont.truetype(
            (self.fonts_dir / "Cantarell-VF.otf").resolve(),
            size=REGULAR_FONT_SIZE,
        )
        font_small = ImageFont.truetype(
            (self.fonts_dir / "Cantarell-VF.otf").resolve(),
            size=SMALL_FONT_SIZE,
        )

        bitmap = Image.open(
            (self.bitmaps_dir / menu.background_bitmap).resolve())
        drawing = ImageDraw.Draw(bitmap)

        children = menu.get_children_as_list()

        try:
            start_child_index = max(
                0,
                children.index(menu.selected_child) - MAX_DISPLAY_ITEMS + 2,
            )
        except ValueError:
            # if there are no children then default to 0
            start_child_index = 0

        end_child_index = start_child_index + MAX_DISPLAY_ITEMS

        for i, child in enumerate(
            children[start_child_index:end_child_index],
        ):
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

            # draw value for MenuItems (calling value callback)
            if isinstance(child, MenuItem) and callable(child.value):
                drawing.text(
                    (193, FIRST_ITEM_BASELINE + LINE_HEIGHT * i),
                    child.value(),
                    fill=font_color,
                    font=font_small,
                    anchor="rs",
                )

            if isinstance(child, MenuItem) and not callable(child.value):
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
        bitmap.paste(listmenu_buttons_bitmap, (self.display.width - 54, 0))
        return bitmap

    def render_tilemenu(self, menu):
        return Image.open((self.bitmaps_dir / menu.background_bitmap).resolve())

    def render_menu(self, menu, partial_refresh=True, invert=False):
        if isinstance(menu, ListMenu):
            bitmap = self.render_listmenu(menu)
        if isinstance(menu, TileMenu):
            bitmap = self.render_tilemenu(menu)
        if invert:
            bitmap = ImageOps.invert(bitmap)
        if partial_refresh:
            self.display.display(
                bitmap,
                update_mode=self.display.PARTIAL_UPDATE,
            )
        else:
            self.display.display(
                bitmap,
                update_mode=self.display.FULL_UPDATE,
            )
