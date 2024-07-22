import logging

from menu import TileMenu, ListMenu
from model import Model
from shapes import Point
from touch import Touch
from TP_lib import epd2in13_V3
from view import View

logging.basicConfig(level=logging.INFO)


class Controller:
    def __init__(self):
        self.touch_flag = False
        self.poll_touch = True

        self.view = View()
        self.model = Model(self.view)
        self.touch = Touch()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Controller: cleaning up")
        # shutdown display
        del self.model
        del self.view

    def print_peripherals(self, peripherals):
        print("printing peripherals:")
        for peripheral in peripherals.values():
            if type(peripheral.rssi) is int and peripheral.rssi < -80:
                continue
            print(peripheral)
        print("\n")

    # def scan_pair_and_connect(self):
    #     bluetoothctl.Power.on()
    #     scan = bluetoothctl.Scan()
    #     scan.scan_on(self.print_peripherals)
    #     scan.scan_off()
    #     uuid = "0C:C4:13:01:CF:59"
    #     device = bluetoothctl.Device(uuid)
    #     device.pair()
    #     device.connect()


def main():
    with Controller() as controller:
        controller.model.current_menu = controller.model.current_menu.children[4]
        controller.model.current_menu.buttons[2].callback()
        controller.model.current_menu.buttons[1].callback()
        controller.model.current_menu.buttons[1].callback()
        controller.model.current_menu.buttons[0].callback()
        controller.model.current_menu = controller.model.current_menu.parent
        controller.model.view.display.frame_queue.join()
        controller.model.view.display.sleep()

        return

        while True:
            if not controller.touch_flag:
                continue

            touch_processed = False

            if not (
                controller.touch_old.X
                and controller.touch_old.Y
                and controller.touch_old.S
                and controller.touch_current.X
                and controller.touch_current.Y
                and controller.touch_current.S
            ):
                continue

            # rotate 90 deg
            touch_point_old = Point(
                epd2in13_V3.EPD_HEIGHT - controller.touch_old.Y[0],
                controller.touch_old.X[0],
            )
            touch_point = Point(
                epd2in13_V3.EPD_HEIGHT - controller.touch_current.Y[0],
                controller.touch_current.X[0],
            )

            if not touch_processed and isinstance(
                controller.model.current_menu, TileMenu
            ):
                for i, touch_target in enumerate(
                    controller.model.current_menu.child_locations
                ):
                    if (
                        touch_target.point1 <= touch_point
                        and touch_point <= touch_target.point2
                    ):
                        controller.model.current_menu = (
                            controller.model.current_menu.children[i]
                        )
                        touch_processed = True
                        break

            if not touch_processed and isinstance(
                controller.model.current_menu, ListMenu
            ):
                for button in controller.model.current_menu.buttons:
                    touch_target = button.location
                    if (
                        touch_target.point1 <= touch_point
                        and touch_point <= touch_target.point2
                    ):
                        button.callback()
                        touch_processed = True
                        break

            # navigate back
            if (
                not touch_processed
                and touch_point_old.x < touch_point.x
                and controller.model.current_menu.parent is not None
            ):
                logging.info("Controller: back swipe")
                controller.model.current_menu = controller.model.current_menu.parent
                touch_processed = True


main()
