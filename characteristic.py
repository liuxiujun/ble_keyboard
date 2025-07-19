# characteristic.py
import dbus
from base import GattCharacteristic, GattDescriptor

# HID Information characteristic
class HIDInformationCharacteristic(GattCharacteristic):
    def __init__(self, bus, index, service):
        GattCharacteristic.__init__(
            self, bus, index,
            '00002A4A-0000-1000-8000-00805f9b34fb',
            ['read'],
            service)
        self.value = [0x01, 0x01, 0x00, 0x03]  # HID v1.1, CountryCode=0, Flags=3

# HID Report Map characteristic
class ReportMapCharacteristic(GattCharacteristic):
    def __init__(self, bus, index, service):
        GattCharacteristic.__init__(
            self, bus, index,
            '00002A4B-0000-1000-8000-00805f9b34fb',
            ['read'],
            service)
        self.value = [
            0x05, 0x01,       # Usage Page (Generic Desktop)
            0x09, 0x06,       # Usage (Keyboard)
            0xA1, 0x01,       # Collection (Application)
            0x05, 0x07,       #   Usage Page (Key Codes)
            0x19, 0xE0,       #   Usage Minimum (224)
            0x29, 0xE7,       #   Usage Maximum (231)
            0x15, 0x00,       #   Logical Minimum (0)
            0x25, 0x01,       #   Logical Maximum (1)
            0x75, 0x01,       #   Report Size (1)
            0x95, 0x08,       #   Report Count (8)
            0x81, 0x02,       #   Input (Data, Variable, Absolute)
            0x95, 0x01,       #   Report Count (1)
            0x75, 0x08,       #   Report Size (8)
            0x81, 0x03,       #   Input (Constant, Variable)
            0x95, 0x05,       #   Report Count (5)
            0x75, 0x01,       #   Report Size (1)
            0x05, 0x08,       #   Usage Page (LEDs)
            0x19, 0x01,       #   Usage Minimum (Num Lock)
            0x29, 0x05,       #   Usage Maximum (Kana)
            0x91, 0x02,       #   Output (Data, Variable, Absolute)
            0x95, 0x01,       #   Report Count (1)
            0x75, 0x03,       #   Report Size (3)
            0x91, 0x03,       #   Output (Constant)
            0x95, 0x06,       #   Report Count (6)
            0x75, 0x08,       #   Report Size (8)
            0x15, 0x00,       #   Logical Minimum (0)
            0x25, 0x65,       #   Logical Maximum (101)
            0x05, 0x07,       #   Usage Page (Key codes)
            0x19, 0x00,       #   Usage Minimum (0)
            0x29, 0x65,       #   Usage Maximum (101)
            0x81, 0x00,       #   Input (Data, Array)
            0xC0              # End Collection
        ]

# Protocol Mode characteristic (Report Mode)
class ProtocolModeCharacteristic(GattCharacteristic):
    def __init__(self, bus, index, service):
        GattCharacteristic.__init__(
            self, bus, index,
            '00002A4E-0000-1000-8000-00805f9b34fb',
            ['read', 'write-without-response'],
            service)
        self.value = [0x01]  # Report Protocol Mode

# Input Report characteristic
class InputReportCharacteristic(GattCharacteristic):
    def __init__(self, bus, index, service):
        GattCharacteristic.__init__(
            self, bus, index,
            '00002A4D-0000-1000-8000-00805f9b34fb',
            ['read', 'notify'],
            service)
        self.value = [0x00] * 8

        # 2902 - Client Characteristic Configuration Descriptor (CCCD)
        self.add_descriptor(GattDescriptor(bus, 0, '2902', ['read', 'write'], self, [0x00, 0x00]))

        # 2908 - Report Reference Descriptor: [Report ID, Report Type]
        self.add_descriptor(GattDescriptor(bus, 1, '2908', ['read'], self, [0x01, 0x01]))

    def send_key_report(self, report):
        self.PropertiesChanged(
            'org.bluez.GattCharacteristic1',
            {'Value': dbus.Array(report, signature='y')},
            []
        )
