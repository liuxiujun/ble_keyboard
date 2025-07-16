# advertisement.py
import dbus
import dbus.service

LE_ADVERTISEMENT_IFACE = "org.bluez.LEAdvertisement1"

class Advertisement(dbus.service.Object):
    def __init__(self, bus, index, advertising_type):
        self.path = f"/org/bluez/example/advertisement{index}"
        self.bus = bus
        self.ad_type = advertising_type
        self.service_uuids = []
        self.manufacturer_data = {}
        self.solicit_uuids = []
        self.service_data = {}
        self.local_name = None
        self.include_tx_power = False
        self.appearance = 0x03C1  # 键盘
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service_uuid(self, uuid):
        self.service_uuids.append(uuid)

    def set_local_name(self, name):
        self.local_name = name

    @dbus.service.method("org.freedesktop.DBus.Properties",
                         in_signature="ss", out_signature="v")
    def Get(self, interface, prop):
        if interface != LE_ADVERTISEMENT_IFACE:
            raise dbus.exceptions.DBusException("org.freedesktop.DBus.Error.InvalidArgs")

        if prop == "Type":
            return self.ad_type
        elif prop == "ServiceUUIDs":
            return dbus.Array(self.service_uuids, signature="s")
        elif prop == "SolicitUUIDs":
            return dbus.Array(self.solicit_uuids, signature="s")
        elif prop == "ManufacturerData":
            return self.manufacturer_data
        elif prop == "ServiceData":
            return self.service_data
        elif prop == "LocalName":
            return self.local_name
        elif prop == "IncludeTxPower":
            return self.include_tx_power
        elif prop == "Appearance":
            return dbus.UInt16(self.appearance)

        raise dbus.exceptions.DBusException("org.freedesktop.DBus.Error.InvalidArgs")

    @dbus.service.method("org.freedesktop.DBus.Properties",
                         in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        if interface != LE_ADVERTISEMENT_IFACE:
            raise dbus.exceptions.DBusException("org.freedesktop.DBus.Error.InvalidArgs")

        props = {
            "Type": self.ad_type,
            "ServiceUUIDs": dbus.Array(self.service_uuids, signature="s"),
            "SolicitUUIDs": dbus.Array(self.solicit_uuids, signature="s"),
            'ManufacturerData': dbus.Dictionary(self.manufacturer_data, signature='qv'),
            'ServiceData': dbus.Dictionary(self.service_data, signature='sv'),
            "LocalName": self.local_name,
            "IncludeTxPower": self.include_tx_power,
            "Appearance": dbus.UInt16(self.appearance),
        }

        return props

    @dbus.service.method(LE_ADVERTISEMENT_IFACE, in_signature="", out_signature="")
    def Release(self):
        print("📡 广播已释放")

