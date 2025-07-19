# characteristic.py
import dbus
from base import GattCharacteristic, GattDescriptor

GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"

# HID Information characteristic
class HIDInformationCharacteristic(GattCharacteristic):
    CHARACTERISTIC_UUID = '2A4A'
    def __init__(self, bus, index, service):
        GattCharacteristic.__init__(
            self, bus, index,
            self.CHARACTERISTIC_UUID,
            ['read'],
            service)
        self.value = [0x01, 0x01, 0x00, 0x03]  # HID v1.1, CountryCode=0, Flags=3

    def ReadValue(self, options):
        print(f'Read HIDInformation: {self.value}')
        return self.value

# HID Report Map characteristic
class ReportMapCharacteristic(GattCharacteristic):
    CHARACTERISTIC_UUID = '2A4B'
    def __init__(self, bus, index, service):
        GattCharacteristic.__init__(
            self, bus, index,
            self.CHARACTERISTIC_UUID,
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
    def ReadValue(self, options):
        print(f'Read ReportMap: {self.value}')
        return self.value


class ControlPointCharacteristic(GattCharacteristic):
    CHARACTERISTIC_UUID = '2A4C'
    def __init__(self, bus, index, service):
        GattCharacteristic.__init__(
                self, bus, index,
                self.CHARACTERISTIC_UUID,
                ["write-without-response"],
                service)
        
        self.value = dbus.Array(bytearray.fromhex('00'), signature=dbus.Signature('y'))

    def WriteValue(self, value, options):
        print(f'Write ControlPoint {value}')
        self.value = value

# Input Report characteristic
class InputReportCharacteristic(GattCharacteristic):
    CHARACTERISTIC_UUID = '2A4D'
    def __init__(self, bus, index, service):
        GattCharacteristic.__init__(
            self, bus, index,
            self.CHARACTERISTIC_UUID,
            ['read', 'notify'],
            service)
        self.value = [0x00] * 8

        # 2902 - Client Characteristic Configuration Descriptor (CCCD)
        self.add_descriptor(GattDescriptor(bus, 0, '2902', ['read', 'write'], self, [0x00, 0x00]))

        # 2908 - Report Reference Descriptor: [Report ID, Report Type]
        self.add_descriptor(GattDescriptor(bus, 1, '2908', ['read'], self, [0x01, 0x01]))

    def send_key_report(self, report):
        """发送按键报告（仅在通知启用时）"""
        print(f"⌨️ 发送 HID 报文: {report}")
        self.value = report
        self.PropertiesChanged(
            'org.bluez.GattCharacteristic1',
            {'Value': dbus.Array(report, signature='y')},
            []
        )

# Protocol Mode characteristic (Report Mode)
class ProtocolModeCharacteristic(GattCharacteristic):
    CHARACTERISTIC_UUID = '2A4E'
    def __init__(self, bus, index, service):
        GattCharacteristic.__init__(
            self, bus, index,
            self.CHARACTERISTIC_UUID,
            ['read', 'write-without-response'],
            service)
        self.value = [0x01]  # Report Protocol Mode

    def ReadValue(self, options):
        print(f'Read ProtocolMode: {self.value}')
        return self.value

    def WriteValue(self, value, options):
        print(f'Write ProtocolMode {value}')
        self.value = value

