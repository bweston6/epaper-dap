import threading
import logging

import safe_exit

from menu import TileMenu, ListMenu
from model import Model
from touch import Touch
from view import View

logging.basicConfig(level=logging.DEBUG)


class Controller:
    def __init__(self):
        self.view = View()
        self.model = Model(self.view)
        self.touch = Touch(
            rotate=90,
            touch_event_gesture_end_callback=self.gesture_handler,
            touch_event_tap_end_callback=self.tap_handler,
        )
        self.exit_event = threading.Event()

        safe_exit.register(self.cleanup)

    def cleanup(self):
        print("Controller: cleaning up")
        self.exit_event.set()

    def tap_handler(self, touch_event):
        if isinstance(self.model.current_menu, TileMenu):
            self.tile_menu_controller(touch_event)
            return
        if isinstance(self.model.current_menu, ListMenu):
            self.list_menu_controller(touch_event)
            return

    def gesture_handler(self, touch_event):
        if (
            touch_event.touch_points[0].x < touch_event.touch_points[-1].x
            and self.model.current_menu.parent is not None
        ):
            logging.info("Controller: back swipe")
            self.model.current_menu = self.model.current_menu.parent

    def tile_menu_controller(self, touch_event):
        for i, touch_target in enumerate(
            self.model.current_menu.child_locations,
        ):
            if touch_target.contains_point(touch_event.touch_points[0]):
                self.model.current_menu = self.model.current_menu.children[i]
                return

    def list_menu_controller(self, touch_event):
        for button in self.model.current_menu.buttons:
            if button.location.contains_point(touch_event.touch_points[0]):
                button.callback()
                return

    # def print_peripherals(self, peripherals):
    #     print("printing peripherals:")
    #     for peripheral in peripherals.values():
    #         if type(peripheral.rssi) is int and peripheral.rssi < -80:
    #             continue
    #         print(peripheral)
    #     print("\n")
    #
    # def scan_pair_and_connect(self):
    #     bluetoothctl.Power.on()
    #     scan = bluetoothctl.Scan()
    #     scan.scan_on(self.print_peripherals)
    #     scan.scan_off()
    #     uuid = "0C:C4:13:01:CF:59"
    #     device = bluetoothctl.Device(uuid)
    #     device.pair()
    #     device.connect()


controller = Controller()
controller.exit_event.wait()
print("Goodbye!")
