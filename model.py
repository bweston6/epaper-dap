from menu import Menu, ListMenu, TileMenu, MenuItem
from shapes import Point, Rectangle
import logging


class Model:
    index = 0
    MAIN_MENU = TileMenu(name="Main Menu", background_bitmap="menu_main.bmp")
    MAIN_MENU.add_children(
        [
            ListMenu(name="Songs"),
            ListMenu(name="Albums"),
            ListMenu(name="Artists"),
            ListMenu(name="Playlists"),
            ListMenu(
                name="Settings",
                background_bitmap="menu_settings.bmp",
            ).add_children(
                [
                    ListMenu(
                        name="Bluetooth",
                        background_bitmap="menu_settings_bluetooth.bmp",
                    ),
                    MenuItem(name="Theme", value="Light"),
                ]
            ),
            TileMenu(name="Now Playing"),
        ]
    )
    MAIN_MENU.child_locations = [
        Rectangle(Point(0, 0), Point(82, 61)),  # songs
        Rectangle(Point(83, 0), Point(166, 61)),  # albums
        Rectangle(Point(167, 0), Point(250, 61)),  # artists
        Rectangle(Point(0, 62), Point(82, 122)),  # playlists
        Rectangle(Point(83, 62), Point(166, 122)),  # settings
        Rectangle(Point(167, 62), Point(250, 122)),  # now playing
    ]

    def __init__(self, view):
        self.view = view
        self.current_menu = self.MAIN_MENU

    @property
    def current_menu(self):
        return self._current_menu

    @current_menu.setter
    def current_menu(self, other):
        assert isinstance(other, Menu)
        self._current_menu = other
        logging.debug(f"Model: navigate to {str(self.current_menu)}")
        self.view.render_menu(self.current_menu)
