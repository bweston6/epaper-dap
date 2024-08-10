from strip_ansi import strip_ansi
import re
import subprocess
import threading


class Peripheral:
    UNPAIRED = 0
    PAIRED = 1
    CONNECTED = 2

    def __init__(self, uuid, name, rssi=None, state=UNPAIRED):
        self.uuid = uuid
        self.name = name
        self.rssi = rssi
        self.state = state

    def __str__(self):
        return f"{self.name} ({self.uuid}) {self.rssi} dB"

    @property
    def rssi(self):
        return self._rssi

    @rssi.setter
    def rssi(self, value):
        if type(value) is str:
            value = int(value)
        self._rssi = value

    def state_to_str(self):
        if self.state == self.UNPAIRED:
            return "pair"
        if self.state == self.PAIRED:
            return "connect"
        if self.state == self.CONNECTED:
            return "disconnect"


class _Discover(threading.Thread):
    def __init__(self, callback, peripherals={}):
        super(_Discover, self).__init__()
        self.callback = callback
        self.peripherals = peripherals
        self.scanning = False
        self.first_scan = True

    def run(self):
        self.scanning = True
        while self.scanning:
            self.callback(self._discover())

    def _update_paired_devices(self):
        for key, value in (
            Device().get_trusted_devices()
            | Device().get_paired_devices()
            | Device().get_connected_devices()
        ).items():
            if key not in self.peripherals:
                self.peripherals[key] = value
            elif self.peripherals[key].state != value.state:
                self.peripherals[key].state = value.state

    def _discover(self, timeout=10):
        if self.first_scan:
            self.first_scan = False
            self._update_paired_devices()
            return self.peripherals

        result = subprocess.run(
            ["bluetoothctl", "--timeout", str(timeout), "scan", "on"],
            capture_output=True,
            check=True,
            text=True,
        )

        # Add new devices to dictionary
        regex = r"NEW.*Device (?P<uuid>[A-F0-9:]*) (?P<name>.*)"
        matches = re.finditer(regex, strip_ansi(result.stdout), re.MULTILINE)
        for match in matches:
            self.peripherals[match.group("uuid")] = Peripheral(
                match.group("uuid"), match.group("name")
            )

        # Update Name
        regex = r"CHG.*Device (?P<uuid>[A-F\d:]{17}) Name: (?P<name>.*)"
        matches = re.finditer(regex, strip_ansi(result.stdout), re.MULTILINE)
        for match in matches:
            if match.group("uuid") in self.peripherals:
                self.peripherals[match.group("uuid")].name = match.group("name")

        # Update RSSI
        regex = r"CHG.*Device (?P<uuid>[A-F\d:]{17}) RSSI:.*?\(?(?P<rssi>-?\d+)\)?$"
        matches = re.finditer(regex, strip_ansi(result.stdout), re.MULTILINE)
        for match in matches:
            if match.group("uuid") in self.peripherals:
                self.peripherals[match.group("uuid")].rssi = match.group("rssi")

        # Delete removed devices
        regex = r"DEL.*Device (?P<uuid>[A-F\d:]{17})"
        matches = re.finditer(regex, strip_ansi(result.stdout), re.MULTILINE)
        for match in matches:
            if match.group("uuid") in self.peripherals:
                self.peripherals.pop(match.group("uuid"))

        self._update_paired_devices()
        return self.peripherals


class Scan:
    def __init__(self):
        self.discover = None

    def scan_on(self, callback):
        self.discover = _Discover(callback)
        self.discover.start()

    def scan_off(self, block=False):
        self.discover.scanning = False
        if block:
            self.discover.join()
        subprocess.run(
            ["bluetoothctl", "scan", "off"],
            stdout=subprocess.DEVNULL,
        )


class Power:
    def on(self):
        subprocess.run(
            ["bluetoothctl", "power", "on"],
            check=True,
            stdout=subprocess.DEVNULL,
        )

    def off(self):
        subprocess.run(
            ["bluetoothctl", "power", "off"],
            check=True,
            stdout=subprocess.DEVNULL,
        )


class Device:
    def __init__(self, uuid=None):
        self.uuid = uuid

    def get_trusted_devices(self):
        trusted_devices = {}

        result = subprocess.run(
            ["bluetoothctl", "devices", "Trusted"],
            capture_output=True,
            check=True,
            text=True,
        )

        # Add new devices to dictionary
        regex = r"Device (?P<uuid>[A-F\d:]{17}) (?P<name>.*)"
        matches = re.finditer(regex, strip_ansi(result.stdout), re.MULTILINE)
        for match in matches:
            trusted_devices[match.group("uuid")] = Peripheral(
                match.group("uuid"), match.group("name"), state=Peripheral.UNPAIRED
            )

        return trusted_devices

    def get_paired_devices(self):
        paired_devices = {}

        result = subprocess.run(
            ["bluetoothctl", "devices", "Paired"],
            capture_output=True,
            check=True,
            text=True,
        )

        # Add new devices to dictionary
        regex = r"Device (?P<uuid>[A-F\d:]{17}) (?P<name>.*)"
        matches = re.finditer(regex, strip_ansi(result.stdout), re.MULTILINE)
        for match in matches:
            paired_devices[match.group("uuid")] = Peripheral(
                match.group("uuid"), match.group("name"), state=Peripheral.PAIRED
            )

        return paired_devices

    def get_connected_devices(self):
        connected_devices = {}

        result = subprocess.run(
            ["bluetoothctl", "devices", "Connected"],
            capture_output=True,
            check=True,
            text=True,
        )

        # Add new devices to dictionary
        regex = r"Device (?P<uuid>[A-F\d:]{17}) (?P<name>.*)"
        matches = re.finditer(regex, strip_ansi(result.stdout), re.MULTILINE)
        for match in matches:
            connected_devices[match.group("uuid")] = Peripheral(
                match.group("uuid"), match.group("name"), state=Peripheral.CONNECTED
            )

        return connected_devices

    def pair(self):
        paired_devices = self.get_paired_devices()

        if self.uuid in paired_devices:
            # device already paired
            return

        subprocess.run(
            ["bluetoothctl", "trust", self.uuid],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        subprocess.run(
            ["bluetoothctl", "pair", self.uuid],
            stdout=subprocess.DEVNULL,
        )

    def connect(self):
        paired_devices = self.get_paired_devices()

        if self.uuid not in paired_devices:
            raise ConnectionRefusedError("Device not paired")

        try:
            subprocess.run(
                ["bluetoothctl", "connect", self.uuid],
                check=True,
                stdout=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            raise ConnectionRefusedError("Connection unsuccessful")

    def disconnect(self):
        connected_devices = self.get_connected_devices()

        if self.uuid not in connected_devices:
            raise ConnectionRefusedError("Device not connected")

        subprocess.run(
            ["bluetoothctl", "disconnect", self.uuid],
            stdout=subprocess.DEVNULL,
        )
