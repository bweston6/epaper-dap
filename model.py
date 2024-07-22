import subprocess
import logging

from menu import Menu, ListMenu, TileMenu, MenuItem
from shapes import Point, Rectangle


class Model:
    def __init__(self, view):
        self.view = view
        self.current_menu = None
        self.invert = False

        self.root_menu = TileMenu(
            model=self, name="Main Menu", background_bitmap="menu_main.bmp"
        )
        self.root_menu.add_children(
            [
                ListMenu(model=self, name="Songs"),
                ListMenu(model=self, name="Albums"),
                ListMenu(model=self, name="Artists"),
                ListMenu(model=self, name="Playlists"),
                ListMenu(
                    model=self,
                    name="Settings",
                    background_bitmap="menu_settings.bmp",
                ).add_children(
                    [
                        ListMenu(
                            model=self,
                            name="Bluetooth",
                            background_bitmap="menu_settings_bluetooth.bmp",
                        ),
                        MenuItem(
                            name="Invert",
                            value=str(self.invert),
                            callback=self.invert_callback,
                        ),
                        MenuItem(
                            name="Shutdown",
                            value="shutdown now",
                            callback=self.shutdown_callback,
                        ),
                    ]
                ),
                TileMenu(model=self, name="Now Playing"),
            ]
        )
        self.root_menu.child_locations = [
            Rectangle(Point(0, 0), Point(82, 61)),  # songs
            Rectangle(Point(83, 0), Point(166, 61)),  # albums
            Rectangle(Point(167, 0), Point(250, 61)),  # artists
            Rectangle(Point(0, 62), Point(82, 122)),  # playlists
            Rectangle(Point(83, 62), Point(166, 122)),  # settings
            Rectangle(Point(167, 62), Point(250, 122)),  # now playing
        ]
        self.current_menu = self.root_menu

    @property
    def current_menu(self):
        return self._current_menu

    @current_menu.setter
    def current_menu(self, other):
        self._current_menu = other
        if isinstance(other, Menu):
            logging.info(f"Model: navigate to {str(self.current_menu)}")
            self.view.render_menu(self.current_menu, invert=self.invert)

    def invert_callback(self):
        self.invert = not self.invert
        self.view.render_menu(self.current_menu, invert=self.invert)

    def shutdown_callback(self):
        subprocess.call(["sudo", "shutdown", "now"])
