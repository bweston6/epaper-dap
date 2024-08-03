from pathlib import Path
import logging

from menu import ListMenu

logger = logging.getLogger(__name__)


class MopidyMenu(ListMenu):
    def __init__(
        self,
        model=None,
        name=None,
        background_bitmap=None,
        icon_path=Path(),
        parent=None,
        selected_child=None,
        uri=None,
    ):
        super().__init__(
            model=model,
            name=name,
            background_bitmap=background_bitmap,
            icon_path=icon_path,
            parent=parent,
            selected_child=selected_child,
        )
        self.children = []
        self.uri = uri

    def __str__(self):
        return f"{type(self)} {self.name} {self.uri}"

    def callback(self):
        if not self.children:
            logger.info("populating children")
            self.populate_children_from_uri()
        self.model.current_menu = self

    def populate_children_from_uri(self):
        refs = self.model.mopidy.library.browse(self.uri)

        for ref in refs:
            self.add_child(
                MopidyMenu(
                    self.model,
                    name=ref.name,
                    background_bitmap="menu_albums_album.bmp",
                    uri=ref.uri,
                )
            )
