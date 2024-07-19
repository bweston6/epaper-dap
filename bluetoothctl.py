from strip_ansi import strip_ansi
import re
import subprocess
import threading


class Peripheral:
    def __init__(self, uuid, name, rssi):
        self.uuid = uuid
        self.name = name
        self.rssi = rssi

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


class _Discover(threading.Thread):
    def __init__(self, callback, peripherals={}):
        super(_Discover, self).__init__()
        self.callback = callback
        self.peripherals = peripherals
        self.scanning = False

    def run(self):
        self.scanning = True
        while self.scanning:
            self.callback(self._discover())

    def _discover(self, timeout=10):
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
                match.group("uuid"), match.group("name"), None
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

        return self.peripherals


class Scan:
    def __init__(self):
        self.discover = None

    def scan_on(self, callback):
        self.discover = _Discover(callback)
        self.discover.start()

    def scan_off(self):
        self.discover.scanning = False
        self.discover.join()


class Power:
    def on():
        subprocess.run(
            ["bluetoothctl", "power", "on"],
            check=True,
            stdout=subprocess.DEVNULL,
        )

    def off():
        subprocess.run(
            ["bluetoothctl", "power", "off"],
            check=True,
            stdout=subprocess.DEVNULL,
        )


class Device:
    def __init__(self, uuid):
        self.uuid = uuid

    def _get_paired_devices(self):
        paired_devices = []

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
            paired_devices.append(match.group("uuid"))

        return paired_devices

    def pair(self):
        paired_devices = self._get_paired_devices()

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
        paired_devices = self._get_paired_devices()

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
