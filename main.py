# main.py
import signal

import dbus
import dbus.mainloop.glib
from dbus import Dictionary, Signature
from gi.repository import GLib

from base import Advertisement, Application
from service import HIDService

BLUEZ_SERVICE_NAME = "org.bluez"


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


def start_periodic_key_press(char):
    def send_key():
        if not char.notifying:
            print("⛔ 尚未订阅 Notify，跳过发送")
            return True  # 等待下一次触发

        # print("⌨️ 发送 HID 报文：A")
        key_down = [0x00, 0x00, 0x04] + [0x00] * 5  # A键
        char.send_key_report(key_down)

        # 1秒后自动释放
        def release_key():
            # print("🔚 发送释放报文")
            char.send_key_report([0x00] * 8)
            return False  # 只执行一次

        GLib.timeout_add(1000, release_key)
        return True  # 继续循环定时器

    # 每 5 秒调用一次 send_key
    GLib.timeout_add_seconds(5, send_key)


def shutdown():
    try:
        print("🛑 正在清理资源...")
        adv_manager.UnregisterAdvertisement(adv.get_path())
        gatt_manager.UnregisterApplication(app.get_path())
    except Exception as e:
        print(f"❌ 清理资源时出错: {e}")
    finally:
        if mainloop.is_running():
            mainloop.quit()


def main():
    global mainloop, gatt_manager, adv_manager, app, adv
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    # adapter = find_adapter(bus)
    adapter_props = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez/hci0"),
        "org.freedesktop.DBus.Properties",
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

    adv = Advertisement(bus, 0, "peripheral")
    adv.add_service_uuid(hid_service.HID_UUID)  # HID Service

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

    # 🧹 尝试清理旧广告（避免重启冲突）
    try:
        adv_manager.UnregisterAdvertisement(adv.get_path())
    except dbus.exceptions.DBusException as e:
        if "org.bluez.Error.DoesNotExist" in str(e):
            pass  # 没有旧广告，跳过
        else:
            print("⚠️ 广播取消异常：", e)
    adv_manager.RegisterAdvertisement(
        adv.get_path(),
        {},
        reply_handler=register_ad_cb,
        error_handler=register_ad_error_cb,
    )

    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, shutdown)
    mainloop = GLib.MainLoop()
    start_periodic_key_press(hid_service.inputReport)
    mainloop.run()


if __name__ == "__main__":
    main()
