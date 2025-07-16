# service.py
import dbus
import dbus.service
import dbus.exceptions

BLUEZ_SERVICE_NAME = 'org.bluez'
GATT_SERVICE_IFACE = 'org.bluez.GattService1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'


class GattService(dbus.service.Object):
    """
    GATT Service 对象（例如 HID 服务）。
    注册路径形如 /org/bluez/example/service0
    """

    def __init__(self, bus, index, uuid, primary):
        self.path = f"/org/bluez/example/service{index}"
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)

    @dbus.service.method(dbus_interface='org.freedesktop.DBus.Properties',
                         in_signature='ss', out_signature='v')
    def Get(self, interface, prop):
        if interface != GATT_SERVICE_IFACE:
            raise dbus.exceptions.DBusException(
                'org.freedesktop.DBus.Error.InvalidArgs')

        if prop == 'UUID':
            return self.uuid
        elif prop == 'Primary':
            return self.primary
        elif prop == 'Characteristics':
            return dbus.Array([c.get_path() for c in self.characteristics], signature='o')

        raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.InvalidArgs')

    @dbus.service.method(dbus_interface='org.freedesktop.DBus.Properties',
                         in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_SERVICE_IFACE:
            raise dbus.exceptions.DBusException(
                'org.freedesktop.DBus.Error.InvalidArgs')

        return {
            'UUID': self.uuid,
            'Primary': self.primary,
            'Characteristics': dbus.Array(
                [c.get_path() for c in self.characteristics], signature='o')
        } 
