# main.py
import dbus
import dbus.mainloop.glib
from dbus import Dictionary, Signature
from gi.repository import GLib

from base import Advertisement, Application
from service import HIDService

BLUEZ_SERVICE_NAME = "org.bluez"

mainloop = None
input_report_char = None


def find_adapter(bus):
    """获取蓝牙适配器路径"""
    obj_manager = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, "/"), "org.freedesktop.DBus.ObjectManager"
    )
    objects = obj_manager.GetManagedObjects()
    for path, interfaces in objects.items():
        if "org.bluez.Adapter1" in interfaces:
            return path
    raise Exception("找不到蓝牙适配器")


def register_ad_cb():
    print("📢 广播注册成功")


def register_ad_error_cb(error):
    print(f"❌ 广播注册失败: {error}")
    mainloop.quit()


def register_app_cb():
    print("✅ GATT 服务注册成功")


def register_app_error_cb(error):
    print(f"❌ GATT 服务注册失败: {error}")
    mainloop.quit()


def send_key_report():
    print("⌨️ 发送 HID 报文：A")
    report = [0x00, 0x00, 0x04] + [0x00] * 5  # A 的 HID code = 0x04
    input_report_char.send_key_report(report)

    # 发送释放按键
    GLib.timeout_add(500, send_key_release)
    return False  # 不重复调用


def send_key_release():
    print("⌨️ 发送释放报文")
    report = [0x00] * 8
    input_report_char.send_key_report(report)
    return False


def main():
    global mainloop, input_report_char
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    adapter = find_adapter(bus)
    adapter_props = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, adapter), "org.freedesktop.DBus.Properties"
    )
    # print(adapter_props.GetAll("org.bluez.Adapter1"))

    adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))

    gatt_manager = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez/hci0"), "org.bluez.GattManager1"
    )
    adv_manager = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez/hci0"),
        "org.bluez.LEAdvertisingManager1",
    )

    app = Application(bus)

    hid_service = HIDService(bus, 0)
    app.add_service(hid_service)

    input_report_char = hid_service.input_report

    adv = Advertisement(bus, 0, "peripheral")
    adv.add_service_uuid("00001812-0000-1000-8000-00805f9b34fb")  # HID Service

    adv.set_local_name("MyBLEKeyboard")
    adv.include_tx_power = True

    print("📡 正在注册 GATT 服务……")

    # for svc in app.services:
    #     print(f"\n📦 Service {svc.uuid} @ {svc.get_path()}")
    #     for ch in svc.characteristics:
    #         print(f"  ├─ Characteristic {ch.uuid} @ {ch.get_path()}")
    #         print(f"     Flags: {ch.flags}")
    #         for desc in getattr(ch, "descriptors", []):
    #             print(f"     └─ Descriptor {desc.uuid} @ {desc.get_path()}")
    #             print(f"        Flags: {desc.flags}")
    #             print(f"        Value: {desc.value}")

    gatt_manager.RegisterApplication(
        app.get_path(),
        {},
        reply_handler=register_app_cb,
        error_handler=register_app_error_cb,
    )
    adv_manager.RegisterAdvertisement(
        adv.get_path(),
        {},
        reply_handler=register_ad_cb,
        error_handler=register_ad_error_cb,
    )

    mainloop = GLib.MainLoop()
    GLib.timeout_add(5000, send_key_report)  # 启动后 5 秒发一个 A
    mainloop.run()


if __name__ == "__main__":
    main()
