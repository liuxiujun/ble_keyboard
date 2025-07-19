import dbus
import dbus.exceptions
import dbus.service

BLUEZ_SERVICE_NAME = "org.bluez"
GATT_SERVICE_IFACE = "org.bluez.GattService1"
GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
GATT_DESC_IFACE = "org.bluez.GattDescriptor1"
LE_ADVERTISEMENT_IFACE = "org.bluez.LEAdvertisement1"

DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
DBUS_PROP_IFACE = "org.freedesktop.DBus.Properties"


class DBusObject(dbus.service.Object):
    def __init__(self, bus, path):
        super().__init__(bus, path)
        self.path = path

    def get_path(self):
        return dbus.ObjectPath(self.path)


class GattService(DBusObject):

    def __init__(self, bus, index, uuid, primary):
        self.path = f"/org/bluez/example/service{index}"
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        super().__init__(self.bus, self.path)

    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)

    def get_characteristic_paths(self):
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result

    @dbus.service.method(
        dbus_interface="org.freedesktop.DBus.Properties",
        in_signature="s",
        out_signature="a{sv}",
    )
    def GetAll(self, interface):
        if interface != GATT_SERVICE_IFACE:
            raise dbus.exceptions.DBusException(
                "org.freedesktop.DBus.Error.InvalidArgs"
            )

        return {
            "UUID": self.uuid,
            "Primary": self.primary,
            "Characteristics": dbus.Array(
                [c.get_path() for c in self.characteristics], signature="o"
            ),
        }

    # @dbus.service.method(
    #     "org.freedesktop.DBus.Introspectable", in_signature="", out_signature="s"
    # )
    # def Introspect(self):
    #     super().Introspect()
    #     return ""


class GattCharacteristic(DBusObject):
    def __init__(self, bus, index, uuid, flags, service):
        self.path = f"{service.get_path()}/char{index}"
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.service = service
        self.descriptors = []
        self.value = []
        self.notifying = False
        super().__init__(self.bus, self.path)

    def add_descriptor(self, descriptor):
        self.descriptors.append(descriptor)

    def get_descriptor_paths(self):
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    @dbus.service.method(
        "org.freedesktop.DBus.Properties", in_signature="ss", out_signature="v"
    )
    def Get(self, interface, prop):
        if interface != GATT_CHRC_IFACE:
            raise dbus.exceptions.DBusException(
                "org.freedesktop.DBus.Error.InvalidArgs"
            )

        if prop == "UUID":
            return self.uuid
        elif prop == "Service":
            return self.service.get_path()
        elif prop == "Flags":
            return dbus.Array(self.flags, signature="s")
        elif prop == "Descriptors":
            return dbus.Array([d.get_path() for d in self.descriptors], signature="o")

        raise dbus.exceptions.DBusException("org.freedesktop.DBus.Error.InvalidArgs")

    @dbus.service.method(
        "org.freedesktop.DBus.Properties", in_signature="s", out_signature="a{sv}"
    )
    def GetAll(self, interface):
        if interface != GATT_CHRC_IFACE:
            raise dbus.exceptions.DBusException(
                "org.freedesktop.DBus.Error.InvalidArgs"
            )

        result = {
            "Service": self.service.get_path(),
            "UUID": self.uuid,
            "Flags": self.flags,
            "Descriptors": dbus.Array(
                [d.get_path() for d in self.descriptors], signature="o"
            ),
        }
        if hasattr(self, "value"):
            result["Value"] = dbus.Array(self.value, signature="y")
        return result

    @dbus.service.method(GATT_CHRC_IFACE, in_signature="a{sv}", out_signature="ay")
    def ReadValue(self, options):
        print("Default ReadValue called, returning error")
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE, in_signature="aya{sv}")
    def WriteValue(self, value, options):
        print("Default WriteValue called, returning error")
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StartNotify(self):
        self.notifying = True
        print("🔔 StartNotify 被调用")

    @dbus.service.method(GATT_CHRC_IFACE)
    def StopNotify(self):
        self.notifying = False
        print("🔕 StopNotify 被调用")

    @dbus.service.signal(GATT_CHRC_IFACE, signature="sa{sv}as")
    def PropertiesChanged(self, interface, changed, invalidated):
        pass

    @dbus.service.signal(DBUS_PROP_IFACE, signature='ay')
    def ReportValueChanged(self, reportValue):
        pass


class GattDescriptor(DBusObject):
    def __init__(self, bus, index, uuid, flags, characteristic, value=None):
        self.path = f"{characteristic.get_path()}/desc{index}"
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.characteristic = characteristic
        self.value = value or []
        super().__init__(self.bus, self.path)

    @dbus.service.method(
        "org.freedesktop.DBus.Properties", in_signature="s", out_signature="a{sv}"
    )
    def GetAll(self, interface):
        if interface != GATT_DESC_IFACE:
            raise dbus.exceptions.DBusException(
                "org.freedesktop.DBus.Error.InvalidArgs"
            )

        return {
            "UUID": self.uuid,
            "Characteristic": self.characteristic.get_path(),
            "Flags": dbus.Array(self.flags, signature="s"),
            "Value": dbus.Array(self.value, signature="y"),
        }

    @dbus.service.method(GATT_DESC_IFACE, in_signature="a{sv}", out_signature="ay")
    def ReadValue(self, options):
        print(f"📘 Read Descriptor {self.uuid}")
        return dbus.Array(self.value, signature="y")

    @dbus.service.method(GATT_DESC_IFACE, in_signature="aya{sv}")
    def WriteValue(self, value, options):
        print(f"📝 Write Descriptor {self.uuid}, value: {value}")
        self.value = value


class Application(DBusObject):

    def __init__(self, bus):
        self.bus = bus
        # self.path = "/org/bluez/example/app"
        self.path = "/"
        self.services = []
        super().__init__(self.bus, self.path)

    def add_service(self, service):
        self.services.append(service)
        service.GetAll("org.bluez.GattService1")

    @dbus.service.method(
        "org.freedesktop.DBus.ObjectManager", out_signature="a{oa{sa{sv}}}"
    )
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = {
                GATT_SERVICE_IFACE: service.GetAll(GATT_SERVICE_IFACE)
            }
            for ch in service.characteristics:
                response[ch.get_path()] = {GATT_CHRC_IFACE: ch.GetAll(GATT_CHRC_IFACE)}

                for desc in ch.descriptors:
                    response[desc.get_path()] = {
                        GATT_DESC_IFACE: desc.GetAll(GATT_DESC_IFACE)
                    }

        return response


class Advertisement(DBusObject):
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
        # dbus.UInt16(961),  # HID Keyboard
        super().__init__(self.bus, self.path)

    def add_service_uuid(self, uuid):
        self.service_uuids.append(uuid)

    def set_local_name(self, name):
        self.local_name = name

    @dbus.service.method(
        "org.freedesktop.DBus.Properties", in_signature="ss", out_signature="v"
    )
    def Get(self, interface, prop):
        if interface != LE_ADVERTISEMENT_IFACE:
            raise dbus.exceptions.DBusException(
                "org.freedesktop.DBus.Error.InvalidArgs"
            )

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

    @dbus.service.method(
        "org.freedesktop.DBus.Properties", in_signature="s", out_signature="a{sv}"
    )
    def GetAll(self, interface):
        if interface != LE_ADVERTISEMENT_IFACE:
            raise dbus.exceptions.DBusException(
                "org.freedesktop.DBus.Error.InvalidArgs"
            )

        props = {
            "Type": self.ad_type,
            "ServiceUUIDs": dbus.Array(self.service_uuids, signature="s"),
            "SolicitUUIDs": dbus.Array(self.solicit_uuids, signature="s"),
            "ManufacturerData": dbus.Dictionary(self.manufacturer_data, signature="qv"),
            "ServiceData": dbus.Dictionary(self.service_data, signature="sv"),
            "LocalName": self.local_name,
            "IncludeTxPower": self.include_tx_power,
            "Appearance": dbus.UInt16(self.appearance),
        }

        return props

    @dbus.service.method(LE_ADVERTISEMENT_IFACE, in_signature="", out_signature="")
    def Release(self):
        print("📡 广播已释放")
