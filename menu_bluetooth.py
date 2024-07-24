from pathlib import Path
import logging

import safe_exit

from menu import ListMenu, MenuItem
import bluetoothctl

logger = logging.getLogger(__name__)


class BluetoothMenu(ListMenu):
    def __init__(
        self,
        model=None,
        name=None,
        background_bitmap=None,
        children={},
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
            selected_child,
        )

        self.scan = bluetoothctl.Scan()
        self.power = bluetoothctl.Power()
        safe_exit.register(self.cleanup)

    def cleanup(self):
        logging.info("cleaning up")
        if self.scan.discover and self.scan.discover.scanning:
            self.scan.scan_off()

    def callback(self):
        self.add_paired_devices_to_children()
        self.add_connected_devices_to_children()
        if self.children:
            self.selected_child = self.get_children_as_list()[0]
        # start scan
        self.power.on()
        self.scan.scan_on(self.update_children)
        self.model.current_menu = self

    def add_paired_devices_to_children(self):
        paired_devices = bluetoothctl.Device()._get_paired_devices()
        for device in paired_devices:
            self.children[device] = MenuItem(device, "connect", self.connect)

    def add_connected_devices_to_children(self):
        connected_devices = bluetoothctl.Device()._get_connected_devices()
        for device in connected_devices:
            self.children[device] = MenuItem(device, "disconnect", self.disconnect)

    def update_children(self, peripherals):
        logger.debug("updating peripherals")
        update_flag = False
        selected_child_index = None

        # save current child index for handling deletions
        if self.children:
            selected_child_index = self.get_children_as_list().index(
                self.selected_child
            )
        self.children = {}

        self.add_paired_devices_to_children()
        self.add_connected_devices_to_children()

        for peripheral in peripherals.values():
            if type(peripheral.rssi) is int and peripheral.rssi < -80:
                continue
            truncated_name = (
                peripheral.name[:16] + "…"
                if len(peripheral.name) > 17
                else peripheral.name
            )
            # update paired devices
            if (
                peripheral.uuid in self.children
                and self.children[peripheral.uuid].name != truncated_name
            ):
                self.children[peripheral.uuid].name = truncated_name
                update_flag = True
            # add new devices
            if peripheral.uuid not in self.children:
                self.children[peripheral.uuid] = MenuItem(
                    truncated_name,
                    "pair",
                    self.pair,
                )
                update_flag = True

        # update selected child if it was deleted
        children_list = self.get_children_as_list()
        if not children_list:
            return

        if selected_child_index is None:
            self.selected_child = children_list[0]
        elif (
            self.selected_child not in children_list
            and len(self.children) > selected_child_index
        ):
            self.selected_child = children_list[selected_child_index]
        elif self.selected_child not in children_list and len(self.children) > 0:
            self.selected_child = self.get_children_as_list()[-1]
        elif self.selected_child not in children_list:
            self.selected_child = None
        elif update_flag:
            # update is automatic if selected_child is updated
            self.model.view.render_menu(
                self.model.current_menu,
                invert=self.model.settings.invert,
            )

    def scan_pair_and_connect(self):
        bluetoothctl.Power.on()
        scan = bluetoothctl.Scan()
        scan.scan_on(self.print_peripherals)
        scan.scan_off()
        uuid = "0C:C4:13:01:CF:59"
        device = bluetoothctl.Device(uuid)
        device.pair()
        device.connect()

    def connect(self):
        uuid = self.get_selected_child_uuid()
        logger.info(f"connect to {uuid}")
        device = bluetoothctl.Device(uuid)
        device.connect()

    def disconnect(self):
        print("Disconnect")

    def pair(self):
        uuid = self.get_selected_child_uuid()
        logger.info(f"pair to {uuid}")
        device = bluetoothctl.Device(uuid)
        device.pair()
        device.connect()

    def get_selected_child_uuid(self):
        return list(self.children.keys())[
            list(self.children.values()).index(self.selected_child)
        ]
