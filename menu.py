from abc import ABCMeta
from pathlib import Path
import logging


def _default_callback():
    logging.warning("MenuItem: callback not implemented")


class Menu(metaclass=ABCMeta):
    def __init__(
        self,
        name=None,
        background_bitmap=None,
        children=[],
        icon_path=Path(),
        parent=None,
    ):
        self.name = name
        self.icon_path = icon_path
        self.children = children
        self.parent = parent
        self.background_bitmap = background_bitmap

    def add_child(self, child):
        assert isinstance(child, Menu) or isinstance(child, MenuItem)
        child.parent = self
        self.children.append(child)

    def add_children(self, children):
        for child in children:
            self.add_child(child)
        return self

    def __str__(self):
        return f"{type(self)} {self.name}"


class ListMenu(Menu):
    def __init__(
        self,
        name=None,
        background_bitmap=None,
        children=[],
        icon_path=Path(),
        parent=None,
        selected_child=None,
    ):
        self.selected_child = selected_child
        super().__init__(
            name,
            background_bitmap,
            children,
            icon_path,
            parent,
        )


class TileMenu(Menu):
    def __init(
        self,
        name=None,
        background_bitmap=None,
        children=[],
        icon_path=Path(),
        parent=None,
        child_locations=[],
    ):
        self.child_locations = child_locations
        super().__init__(
            name,
            background_bitmap,
            children,
            icon_path,
            parent,
        )


class MenuItem:
    def __init__(
        self,
        name=None,
        value=None,
        callback=_default_callback,
        parent=None,
    ):
        self.name = name
        self.value = value
        self.callback = callback
        self.parent = parent

    def __str__(self):
        return f"{type(self)} {self.name}"
