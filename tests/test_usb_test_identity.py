from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]

FIRMWARE_IDENTITY_FILES = (
    "workspace/preflight/usb_config.h",
    "workspace/exercises/01_macro_keyboard/usb_config.h",
    "workspace/exercises/02_rotary_cursor_size/usb_config.h",
    "workspace/exercises/03_vibration_motor_console/usb_config.h",
    "workspace/exercises/04_rotary_cursor_haptic/usb_config.h",
    "workspace/poc/joystick_mouse_poc/usb_config.h",
    "workspace/poc/ir_send_poc/usb_config.h",
    "workspace/poc/ir_recv_poc/usb_config.h",
    "workspace/poc/oled_poc/usb_config.h",
    "workspace/poc/ws2812b8_hid_poc/usb_config.h",
    "workspace/poc/vibration_motor_hid/src/usb_config.h",
)

HOST_IDENTITY_FILES = (
    "workspace/preflight/host/preflight_hid.py",
    "workspace/exercises/01_macro_keyboard/host/hidcheck.py",
    "workspace/exercises/02_rotary_cursor_size/host/cursor_size_host.py",
    "workspace/exercises/03_vibration_motor_console/host/motorctl.py",
    "workspace/exercises/04_rotary_cursor_haptic/host/cursor_size_host.py",
    "workspace/poc/joystick_mouse_poc/host/joystick_mouse_host.py",
    "workspace/poc/ir_send_poc/host/ir_send_host.py",
    "workspace/poc/ir_recv_poc/host/ir_recv_host.py",
    "workspace/poc/oled_poc/host/oled_host.py",
    "workspace/poc/ws2812b8_hid_poc/host/ws2812b8_host.py",
    "workspace/poc/vibration_motor_hid/host/motorctl.py",
)


class UsbTestIdentityTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_firmware_uses_shared_test_identity_and_warning(self) -> None:
        for relative_path in FIRMWARE_IDENTITY_FILES:
            with self.subTest(path=relative_path):
                source = self.read(relative_path)
                self.assertIn("#define UIAP_USB_VID 0x1209", source)
                self.assertIn("#define UIAP_USB_PID 0x0001", source)
                self.assertIn("TEST-ONLY USB IDENTIFIER", source)
                self.assertIn("not globally unique", source)
                self.assertIn("manufacturing", source)
                self.assertIn("redistribution", source)

    def test_host_uses_shared_test_identity_and_warning(self) -> None:
        for relative_path in HOST_IDENTITY_FILES:
            with self.subTest(path=relative_path):
                source = self.read(relative_path)
                self.assertIn("VID = 0x1209", source)
                self.assertIn("PID = 0x0001", source)
                self.assertIn("TEST-ONLY USB IDENTIFIER", source)
                self.assertIn("not globally unique", source)
                self.assertIn("manufacturing", source)
                self.assertIn("redistribution", source)


if __name__ == "__main__":
    unittest.main()
