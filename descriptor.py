# descriptor.py
import dbus
import dbus.service
import dbus.exceptions

GATT_DESC_IFACE = 'org.bluez.GattDescriptor1'

class GattDescriptor(dbus.service.Object):
    def __init__(self, bus, index, uuid, flags, characteristic, value=None):
        self.path = f"{characteristic.get_path()}/desc{index}"
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.characteristic = characteristic
        self.value = value or []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method("org.freedesktop.DBus.Properties", in_signature='ss', out_signature='v')
    def Get(self, interface, prop):
        if interface != GATT_DESC_IFACE:
            raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.InvalidArgs')

        if prop == 'UUID':
            return self.uuid
        elif prop == 'Characteristic':
            return self.characteristic.get_path()
        elif prop == 'Flags':
            return dbus.Array(self.flags, signature='s')
        elif prop == 'Value':
            return dbus.Array(self.value, signature='y')

        raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.InvalidArgs')

    @dbus.service.method("org.freedesktop.DBus.Properties", in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_DESC_IFACE:
            raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.InvalidArgs')

        return {
            'UUID': self.uuid,
            'Characteristic': self.characteristic.get_path(),
            'Flags': dbus.Array(self.flags, signature='s'),
            'Value': dbus.Array(self.value, signature='y')
        }

    @dbus.service.method(GATT_DESC_IFACE, in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):
        print(f"📘 Read Descriptor {self.uuid}")
        return dbus.Array(self.value, signature='y')

    @dbus.service.method(GATT_DESC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print(f"📝 Write Descriptor {self.uuid}, value: {value}")
        self.value = value

