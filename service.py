# service.py
import dbus
import dbus.exceptions
import dbus.service

from base import GattService
from characteristic import (
    HIDInformationCharacteristic,
    ControlPointCharacteristic,
    InputReportCharacteristic,
    ProtocolModeCharacteristic,
    ReportMapCharacteristic,
)


class HIDService(GattService):
    HID_UUID = "1812"

    def __init__(self, bus, index):
        GattService.__init__(self, bus, index, self.HID_UUID, True)

        self.protocolMode = ProtocolModeCharacteristic(bus, 0, self)
        self.hidInformation = HIDInformationCharacteristic(bus, 1, self)
        self.controlPoint = ControlPointCharacteristic(bus, 2, self)
        self.inputReport = InputReportCharacteristic(bus, 3, self)
        self.reportMap = ReportMapCharacteristic(bus, 4,self)

        self.add_characteristic(self.protocolMode)
        self.add_characteristic(self.hidInformation)
        self.add_characteristic(self.controlPoint)
        self.add_characteristic(self.inputReport)
        self.add_characteristic(self.reportMap)
