from abc import ABCMeta
from pathlib import Path
import logging
from shapes import Rectangle, Point


def _default_callback():
    logging.warning("MenuItem: callback not implemented")


class Menu(metaclass=ABCMeta):
    def __init__(
        self,
        name=None,
        background_bitmap=None,
        model=None,
        children=[],
        icon_path=Path(),
        parent=None,
    ):
        self.name = name
        self.icon_path = icon_path
        self.children = children
        self.parent = parent
        self.background_bitmap = background_bitmap

    def __str__(self):
        return f"{type(self)} {self.name}"

    def add_child(self, child):
        assert isinstance(child, Menu) or isinstance(child, MenuItem)
        child.parent = self
        self.children.append(child)

    def add_children(self, children):
        for child in children:
            self.add_child(child)
        return self

    def callback(self):
        self.model.current_menu = self


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
        super().__init__(
            name,
            background_bitmap,
            children,
            icon_path,
            parent,
        )

        self.selected_child = selected_child
        if self.selected_child is None:
            self.selected_child = self.children[0]

        self.buttons = [
            Button(
                "up",
                Rectangle(Point(196, 6), Point(196 + 54, 6 + 36)),
                self.select_next,
            ),
            Button(
                "select",
                Rectangle(Point(196, 43), Point(196 + 54, 43 + 35)),
                self.selected_child_callback,
            ),
            Button(
                "down",
                Rectangle(Point(196, 79), Point(196 + 54, 79 + 36)),
                self.select_previous,
            ),
        ]

    def select_next(self):
        next_child_index = self.children.index(self.selected_child) + 1
        self.selected_child = self.children[
            max(next_child_index, len(self.children - 1))
        ]

    def select_previous(self):
        prev_child_index = self.children.index(self.selected_child) - 1
        self.selected_child = self.children[
            min(prev_child_index, len(self.children - 1))
        ]

    def selected_child_callback(self):
        self.selected_child.callback()
        return


class TileMenu(Menu):
    def __init__(
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


class Button:
    def __init__(self, name=None, location=Rectangle, callback=None):
        self.name = name
        self.location = location
        self.callback = callback
