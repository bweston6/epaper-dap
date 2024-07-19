# import lib.bluetoothctl as bluetoothctl
from TP_lib import epd2in13_V3
from TP_lib import gt1151
from menu import TileMenu, ListMenu
from model import Model
from shapes import Point
from view import View
import logging
import threading
import time

logging.basicConfig(level=logging.DEBUG)


class Controller:
    def __init__(self):
        self.touch_flag = False
        self.poll_touch = True

        self.display = epd2in13_V3.EPD()

        self.gt = gt1151.GT1151()
        self.gt.GT_Init()

        self.touch_current = gt1151.GT_Development()
        self.touch_old = gt1151.GT_Development()

        # init touch thread
        self.touch_handler_thread = threading.Thread(
            target=self.touch_handler,
        )
        # self.touch_handler_thread.daemon = True
        self.touch_handler_thread.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Controller: cleaning up")
        # stop touch handler thread
        self.poll_touch = False
        self.touch_handler_thread.join()

        # shutdown display
        self.display.sleep()
        self.display.Dev_exit()

    def touch_handler(self):
        logging.debug("Controller: set_touch_flag started")
        touch_irq_pin = self.gt.INT
        while self.poll_touch:
            # active low
            irq = not self.gt.digital_read(touch_irq_pin)
            self.touch_current.Touch = irq
            self.touch_flag = irq
            self.gt.GT_Scan(self.touch_current, self.touch_old)

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
        view = View(controller.display)
        model = Model(view)
        while True:
            if time.time() - controller.touch_current.timestamp > 1:
                continue
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

            if isinstance(model.current_menu, TileMenu):
                for i, touch_target in enumerate(model.current_menu.child_locations):
                    if (
                        touch_target.point1 <= touch_point
                        and touch_point <= touch_target.point2
                    ):
                        selected_menu = model.current_menu.children[i]
                model.current_menu = selected_menu
                continue

            if isinstance(model.current_menu, ListMenu):
                pass

            # navigate back
            if (
                controller.touch_current.timestamp - controller.touch_old.timestamp
                < 100
                and touch_point_old.x < touch_point.x
                and model.current_menu.parent is not None
            ):
                model.current_menu = model.current_menu.parent
                continue


main()
