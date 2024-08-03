import logging

from menu import Menu, ListMenu, TileMenu, MenuItem
from menu_bluetooth import BluetoothMenu
from menu_mopidy import MopidyMenu
from model_mopidy import Mopidy
from model_settings import Settings
from shapes import Point, Rectangle

logger = logging.getLogger(__name__)


class Model:
    def __init__(self, view):
        # vars
        self.view = view
        self.current_menu = None

        # sub-models
        self.settings = Settings(self)
        self.mopidy = Mopidy(self)

        # menu tree
        self.root_menu = TileMenu(
            model=self, name="Main Menu", background_bitmap="menu_main.bmp"
        )
        self.root_menu.add_children(
            [
                MopidyMenu(
                    model=self,
                    name="Songs",
                    uri="local:directory?type=track",
                    background_bitmap="menu_albums.bmp",
                ),
                MopidyMenu(
                    model=self,
                    name="Albums",
                    uri="local:directory?type=album",
                    background_bitmap="menu_albums.bmp",
                ),
                MopidyMenu(
                    model=self,
                    name="Artists",
                    uri="local:directory?type=artist&role=albumartist",
                    background_bitmap="menu_albums.bmp",
                ),
                ListMenu(model=self, name="Playlists"),
                ListMenu(
                    model=self,
                    name="Settings",
                    background_bitmap="menu_settings.bmp",
                ).add_children(
                    [
                        BluetoothMenu(
                            model=self,
                            name="Bluetooth",
                            background_bitmap="menu_settings_bluetooth.bmp",
                        ),
                        MenuItem(
                            name="Theme",
                            value=self.settings.invert_value_callback,
                            callback=self.settings.invert_callback,
                        ),
                        MenuItem(
                            name="Shutdown",
                            value="sudo shutdown now",
                            callback=self.settings.shutdown_callback,
                        ),
                        MenuItem(
                            name="Reboot",
                            value="sudo reboot",
                            callback=self.settings.reboot_callback,
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
            logger.info(f"navigate to {str(self.current_menu)}")
            self.view.render_menu(
                self.current_menu,
                invert=self.settings.invert,
            )
