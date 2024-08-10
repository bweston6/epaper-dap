from abc import ABCMeta
from pathlib import Path
from types import NoneType
import logging

from shapes import Rectangle, Point

logger = logging.getLogger(__name__)


def _default_callback():
    logger.warning("callback not implemented")


class Menu(metaclass=ABCMeta):
    def __init__(
        self,
        model=None,
        name=None,
        background_bitmap=None,
        children=[],
        icon_path=Path(),
        parent=None,
    ):
        self.model = model
        self.name = name
        self.background_bitmap = background_bitmap
        self.children = children
        self.icon_path = icon_path
        self.parent = parent

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

    def get_children_as_list(self):
        if isinstance(self.children, dict):
            return list(self.children.values())
        if isinstance(self.children, list):
            return self.children


class ListMenu(Menu):
    def __init__(
        self,
        model=None,
        name=None,
        background_bitmap=None,
        children=[],
        icon_path=Path(),
        parent=None,
        selected_child=None,
    ):
        super().__init__(
            model,
            name,
            background_bitmap,
            children,
            icon_path,
            parent,
        )

        self.selected_child = selected_child

        if self.selected_child is None and self.children:
            self.selected_child = self.get_children_as_list()[0]

        self.buttons = [
            Button(
                "up",
                Rectangle(Point(196, 6), Point(196 + 54, 6 + 36)),
                self.select_previous,
            ),
            Button(
                "select",
                Rectangle(Point(196, 43), Point(196 + 54, 43 + 35)),
                self.selected_child_callback,
            ),
            Button(
                "down",
                Rectangle(Point(196, 79), Point(196 + 54, 79 + 36)),
                self.select_next,
            ),
        ]

    @property
    def selected_child(self):
        return self._selected_child

    @selected_child.setter
    def selected_child(self, other):
        assert isinstance(other, (NoneType, Menu, MenuItem))
        self._selected_child = other
        if self is self.model.current_menu:
            logger.info(f"select {str(self.selected_child)}")
            self.model.view.render_menu(
                self.model.current_menu, invert=self.model.settings.invert
            )

    def add_child(self, child):
        super().add_child(child)
        if self.selected_child not in self.children:
            self.selected_child = self.children[0]

    def select_next(self):
        logger.info("select_next")
        children = self.get_children_as_list()
        next_child_index = children.index(self.selected_child) + 1
        self.selected_child = children[min(next_child_index, len(children) - 1)]

    def select_previous(self):
        if len(self.children) == 0:
            return
        logger.info("select_previous")
        children = self.get_children_as_list()
        prev_child_index = children.index(self.selected_child) - 1
        self.selected_child = children[max(prev_child_index, 0)]

    def selected_child_callback(self):
        if self.selected_child is None:
            return
        logger.info(f"calling callback for {str(self.selected_child)}")
        self.selected_child.callback()
        return


class TileMenu(Menu):
    def __init__(
        self,
        model=None,
        name=None,
        background_bitmap=None,
        child_locations=[],
        children=[],
        icon_path=Path(),
        parent=None,
    ):
        super().__init__(
            model,
            name,
            background_bitmap,
            children,
            icon_path,
            parent,
        )
        self.child_locations = child_locations


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
