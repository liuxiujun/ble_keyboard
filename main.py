# main.py
import dbus
import dbus.mainloop.glib
from gi.repository import GLib

from advertisement import Advertisement
from characteristic import GattCharacteristic
from descriptor import GattDescriptor
from service import GattService

BLUEZ_SERVICE_NAME = "org.bluez"
ADAPTER_INTERFACE = "org.bluez.Adapter1"
GATT_MANAGER_INTERFACE = "org.bluez.GattManager1"
LE_ADVERTISING_MANAGER_INTERFACE = "org.bluez.LEAdvertisingManager1"

GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE = 'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE = 'org.bluez.GattDescriptor1'

# 标准键盘 Report Map（带 Report ID 1）
REPORT_MAP = [
    0x05, 0x01,  # Usage Page (Generic Desktop)
    0x09, 0x06,  # Usage (Keyboard)
    0xA1, 0x01,  # Collection (Application)
    0x05, 0x07,  #   Usage Page (Key Codes)
    0x19, 0xE0,  #   Usage Min (224)
    0x29, 0xE7,  #   Usage Max (231)
    0x15, 0x00,  #   Logical Min (0)
    0x25, 0x01,  #   Logical Max (1)
    0x75, 0x01,  #   Report Size (1)
    0x95, 0x08,  #   Report Count (8)
    0x81, 0x02,  #   Input (Data, Var, Abs)
    0x95, 0x01,  #   Report Count (1)
    0x75, 0x08,  #   Report Size (8)
    0x81, 0x01,  #   Input (Const)
    0x95, 0x06,  #   Report Count (6)
    0x75, 0x08,  #   Report Size (8)
    0x15, 0x00,  #   Logical Min (0)
    0x25, 0x65,  #   Logical Max (101)
    0x05, 0x07,  #   Usage Page (Key Codes)
    0x19, 0x00,  #   Usage Min (0)
    0x29, 0x65,  #   Usage Max (101)
    0x81, 0x00,  #   Input (Data, Array)
    0xC0,  # End Collection
]

mainloop = None
input_report_char = None


def find_adapter(bus):
    """获取蓝牙适配器路径"""
    obj_manager = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, "/"), "org.freedesktop.DBus.ObjectManager"
    )
    objects = obj_manager.GetManagedObjects()
    for path, interfaces in objects.items():
        if ADAPTER_INTERFACE in interfaces:
            return path
    raise Exception("找不到蓝牙适配器")


def register_app_cb():
    print("✅ GATT 服务注册成功")


def register_app_error_cb(error):
    print("❌ GATT 服务注册失败:", str(error))
    mainloop.quit()


def register_ad_cb():
    print("📢 广播注册成功")


def register_ad_error_cb(error):
    print("❌ 广播注册失败:", str(error))
    mainloop.quit()


def send_key_report():
    print("⌨️ 发送 HID 报文：A")

    # “A” 键：HID 键码为 0x04，Modifier 为 0x00
    report = [0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00]  # Press A
    input_report_char.value = report

    input_report_char.PropertiesChanged(
        "org.bluez.GattCharacteristic1",
        {"Value": dbus.Array(report, signature="y")},
        [],
    )

    # 发送释放键（全部为 0）
    GLib.timeout_add(200, send_key_release)
    return False  # 只触发一次


def send_key_release():
    print("⌨️ 发送释放报文")
    report = [0x00] * 8
    input_report_char.value = report
    input_report_char.PropertiesChanged(
        "org.bluez.GattCharacteristic1",
        {"Value": dbus.Array(report, signature="y")},
        [],
    )
    return False


class Application(dbus.service.Object):
    """
    整个 GATT 应用容器，包含多个 GATT 服务。
    """

    def __init__(self, bus):
        self.path = "/"
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)

    def add_service(self, service):
        self.services.append(service)
        service.GetAll("org.bluez.GattService1")


    def get_path(self):
        return dbus.ObjectPath(self.path)

    # @dbus.service.method(
    #     "org.freedesktop.DBus.ObjectManager", out_signature="a{oa{sa{sv}}}"
    # )
    # def GetManagedObjects(self):
    #     response = {}
    #     for service in self.services:
    #         response[service.get_path()] = {
    #             "org.bluez.GattService1": {
    #                 "UUID": service.uuid,
    #                 "Primary": service.primary,
    #                 "Characteristics": dbus.Array(
    #                     [c.get_path() for c in service.characteristics], signature="o"
    #                 ),
    #             }
    #         }
    #         for chrc in service.characteristics:
    #             response[chrc.get_path()] = {
    #                 "org.bluez.GattCharacteristic1": {
    #                     "UUID": chrc.uuid,
    #                     "Service": service.get_path(),
    #                     "Flags": dbus.Array(chrc.flags, signature="s"),
    #                     "Descriptors": dbus.Array(
    #                         [d.get_path() for d in chrc.descriptors], signature="o"
    #                     ),
    #                 }
    #             }
    #             for desc in chrc.descriptors:
    #                 response[desc.get_path()] = {
    #                     "org.bluez.GattDescriptor1": {
    #                         "UUID": desc.uuid,
    #                         "Characteristic": chrc.get_path(),
    #                         "Flags": dbus.Array(desc.flags, signature="s"),
    #                         "Value": dbus.Array(desc.value, signature="y"),
    #                     }
    #                 }
    #     return response
    @dbus.service.method("org.freedesktop.DBus.ObjectManager", out_signature="a{oa{sa{sv}}}")
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] =  { GATT_SERVICE_IFACE: service.GetAll(GATT_SERVICE_IFACE) }
            for ch in service.characteristics:
                response[ch.get_path()] = { GATT_CHRC_IFACE: ch.GetAll(GATT_CHRC_IFACE) }
                for desc in ch.descriptors:
                    response[desc.get_path()] = { GATT_DESC_IFACE: desc.GetAll(GATT_DESC_IFACE) }
        return response

def main():
    global mainloop, input_report_char
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    adapter_path = find_adapter(bus)

    # 创建 GATT 应用
    app = Application(bus)

    # 创建服务（以 HID 示例：UUID 0x1812）
    hid_service = GattService(bus, 0, "00001812-0000-1000-8000-00805f9b34fb", True)

    # HID Information 
    hid_info_char = GattCharacteristic(
        bus,
        index=0,
        uuid="00002A4A-0000-1000-8000-00805f9b34fb",
        flags=["read"],
        service=hid_service,
    )
    hid_info_char.value = [
        0x11,
        0x01,
        0x00,
        0x02,
    ]  # version 1.11, no country, flags = 2
    hid_service.add_characteristic(hid_info_char)

    # Report Map 特征
    report_map_char = GattCharacteristic(
        bus,
        index=1,
        uuid="00002A4B-0000-1000-8000-00805f9b34fb",
        flags=["read"],
        service=hid_service,
    )
    report_map_char.value = REPORT_MAP
    hid_service.add_characteristic(report_map_char)

    # Input Report
    input_report_char = GattCharacteristic(
        bus,
        index=2,
        uuid="00002A4D-0000-1000-8000-00805f9b34fb",
        flags=["read", "notify"],
        service=hid_service,
    )
    input_report_char.value = [0x00] * 8  # 初始 HID 报文，8 字节

    cccd = GattDescriptor(
        bus,
        index=0,
        uuid="2902",
        flags=["read", "write"],
        characteristic=input_report_char,
        value=[0x00, 0x00],
    )
    input_report_char.add_descriptor(cccd)

    report_ref_desc = GattDescriptor(
        bus,
        index=1,
        uuid="2908",
        flags=["read"],
        characteristic=input_report_char,
        value=[0x01, 0x01],  # Report ID = 1, Report Type = Input
    )
    input_report_char.add_descriptor(report_ref_desc)

    hid_service.add_characteristic(input_report_char)

    app.add_service(hid_service)

    # 注册 GATT 服务
    gatt_manager = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, adapter_path), GATT_MANAGER_INTERFACE
    )

    print("📡 正在注册 GATT 服务……")
    gatt_manager.RegisterApplication(
        app.get_path(),
        {},
        reply_handler=register_app_cb,
        error_handler=register_app_error_cb,
    )

    # 注册 Advertisement 广告
    ad = Advertisement(bus, index=0, advertising_type="peripheral")
    ad.set_local_name("MyBLEKeyboard")
    ad.add_service_uuid("00001812-0000-1000-8000-00805f9b34fb")  # HID Service

    ad_manager = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, adapter_path),
        LE_ADVERTISING_MANAGER_INTERFACE,
    )
    ad_manager.RegisterAdvertisement(
        ad.get_path(),
        {},
        reply_handler=register_ad_cb,
        error_handler=register_ad_error_cb,
    )

    GLib.timeout_add(5000, send_key_report)  # 启动后 5 秒发一个 A
    mainloop = GLib.MainLoop()
    mainloop.run()


if __name__ == "__main__":
    main()
