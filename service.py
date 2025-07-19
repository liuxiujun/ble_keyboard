# service.py
import dbus
import dbus.exceptions
import dbus.service

from base import GattService
from characteristic import (
    HIDInformationCharacteristic,
    InputReportCharacteristic,
    ProtocolModeCharacteristic,
    ReportMapCharacteristic,
)


class HIDService(GattService):
    HID_UUID = "00001812-0000-1000-8000-00805f9b34fb"

    def __init__(self, bus, index):
        GattService.__init__(self, bus, index, self.HID_UUID, True)

        self.add_characteristic(HIDInformationCharacteristic(bus, 0, self))
        self.add_characteristic(ReportMapCharacteristic(bus, 1, self))
        self.add_characteristic(ProtocolModeCharacteristic(bus, 2, self))
        self.input_report = InputReportCharacteristic(bus, 3, self)
        self.add_characteristic(self.input_report)
