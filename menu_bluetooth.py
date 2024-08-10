from pathlib import Path
import collections
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
        children=collections.OrderedDict(),
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
        if self.children:
            self.selected_child = self.get_children_as_list()[0]
        # start scan
        self.power.on()
        self.scan.scan_on(self.update_children)
        self.model.current_menu = self

    def _update_existing_child(self, peripheral):
        update_flag = False

        if self.children[peripheral.uuid].name != peripheral.name:
            self.children[peripheral.uuid].name = peripheral.name
            update_flag = True

        if self.children[peripheral.uuid].value != peripheral.state_to_str():
            match self.children[peripheral.uuid].value:
                case "connecting" | "disconnecting" | "pairing":
                    # don't update when action is in-progress
                    return update_flag
                case _:
                    self.children[peripheral.uuid].value = peripheral.state_to_str()
                    self._update_child_callback_from_peripheral_state(peripheral)
            update_flag = True

        return update_flag

    def _update_child_callback_from_peripheral_state(self, peripheral):
        match peripheral.state:
            case bluetoothctl.Peripheral.UNPAIRED:
                self.children[peripheral.uuid].callback = self.pair
            case bluetoothctl.Peripheral.PAIRED:
                self.children[peripheral.uuid].callback = self.connect
            case bluetoothctl.Peripheral.CONNECTED:
                self.children[peripheral.uuid].callback = self.disconnect

    def _insert_new_child(self, peripheral):
        match peripheral.state:
            case bluetoothctl.Peripheral.UNPAIRED:
                self.children[peripheral.uuid] = MenuItem(
                    peripheral.name,
                    peripheral.state_to_str(),
                    self.pair,
                )
            case bluetoothctl.Peripheral.PAIRED:
                self.children[peripheral.uuid] = MenuItem(
                    peripheral.name,
                    peripheral.state_to_str(),
                    self.connect,
                )
            case bluetoothctl.Peripheral.CONNECTED:
                self.children[peripheral.uuid] = MenuItem(
                    peripheral.name,
                    peripheral.state_to_str(),
                    self.disconnect,
                )

    def update_children(self, peripherals):
        logger.debug("updating peripherals")
        update_flag = False
        selected_child_index = None

        # save current child index for handling deletions
        if self.children:
            selected_child_index = self.get_children_as_list().index(
                self.selected_child
            )

        # insert/update children
        for peripheral in peripherals.values():
            if type(peripheral.rssi) is int and peripheral.rssi < -80:
                continue
            # update existing children
            if peripheral.uuid in self.children:
                update_flag |= self._update_existing_child(peripheral)
            # insert new children
            if peripheral.uuid not in self.children:
                self._insert_new_child(peripheral)
                update_flag = True

        # remove stale children
        for uuid in self.children.copy().keys():
            if uuid not in peripherals:
                del self.children[uuid]

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
        self.selected_child.value = "connecting"
        self.selected_child.callback = None
        self.model.view.render_menu(
            self.model.current_menu,
            invert=self.model.settings.invert,
        )
        device = bluetoothctl.Device(uuid)
        try:
            device.connect()
            self.selected_child.value = "connected"
            self.children.move_to_end(
                self.get_selected_child_uuid(),
                last=False,
            )
        except ConnectionError:
            self.selected_child.value = "unsuccessful"
        self.model.view.render_menu(
            self.model.current_menu,
            invert=self.model.settings.invert,
        )

    def disconnect(self):
        uuid = self.get_selected_child_uuid()
        logger.info(f"disconnect from {uuid}")
        self.selected_child.value = "disconnecting"
        self.selected_child.callback = None
        self.model.view.render_menu(
            self.model.current_menu,
            invert=self.model.settings.invert,
        )
        device = bluetoothctl.Device(uuid)
        device.disconnect()
        self.selected_child.value = "disconnected"
        self.model.view.render_menu(
            self.model.current_menu,
            invert=self.model.settings.invert,
        )

    def pair(self):
        uuid = self.get_selected_child_uuid()
        logger.info(f"pair to {uuid}")
        self.selected_child.value = "pairing"
        self.selected_child.callback = None
        self.model.view.render_menu(
            self.model.current_menu,
            invert=self.model.settings.invert,
        )
        device = bluetoothctl.Device(uuid)
        device.pair()
        self.connect()

    def get_selected_child_uuid(self):
        return list(self.children.keys())[
            list(self.children.values()).index(self.selected_child)
        ]
