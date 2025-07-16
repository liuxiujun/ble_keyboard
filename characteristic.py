# characteristic.py
import dbus
import dbus.service
import dbus.exceptions

DBUS_PROP_IFACE =    'org.freedesktop.DBus.Properties'

GATT_CHRC_IFACE = 'org.bluez.GattCharacteristic1'

class GattCharacteristic(dbus.service.Object):
    def __init__(self, bus, index, uuid, flags, service):
        self.path = f"{service.get_path()}/char{index}"
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.service = service
        self.descriptors = []
        self.value = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_descriptor(self, descriptor):
        self.descriptors.append(descriptor)

    @dbus.service.method("org.freedesktop.DBus.Properties", in_signature='ss', out_signature='v')
    def Get(self, interface, prop):
        if interface != GATT_CHRC_IFACE:
            raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.InvalidArgs')

        if prop == 'UUID':
            return self.uuid
        elif prop == 'Service':
            return self.service.get_path()
        elif prop == 'Flags':
            return dbus.Array(self.flags, signature='s')
        elif prop == 'Descriptors':
            return dbus.Array([d.get_path() for d in self.descriptors], signature='o')

        raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.InvalidArgs')

    @dbus.service.method("org.freedesktop.DBus.Properties", in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_CHRC_IFACE:
            raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.InvalidArgs')

        return {
            'UUID': self.uuid,
            'Service': self.service.get_path(),
            'Flags': dbus.Array(self.flags, signature='s'),
            'Descriptors': dbus.Array([d.get_path() for d in self.descriptors], signature='o')
        }

    @dbus.service.method(GATT_CHRC_IFACE, in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):
        print(f"🔹 Read request on {self.uuid}")
        return dbus.Array(self.value, signature='y')

    @dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print(f"🔸 Write request on {self.uuid}, data: {value}")
        self.value = value
 
    @dbus.service.signal(GATT_CHRC_IFACE, signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass
    
    # @dbus.service.method(GATT_CHRC_IFACE)
    # def StartNotify(self):
    #     print('Default StartNotify called, returning error')
    #     raise NotSupportedException()
    #
    # @dbus.service.method(GATT_CHRC_IFACE)
    # def StopNotify(self):
    #     print('Default StopNotify called, returning error')
    #     raise NotSupportedException()

    @dbus.service.signal(DBUS_PROP_IFACE,
                         signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass


