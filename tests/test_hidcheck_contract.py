from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
from io import StringIO
from pathlib import Path
import re
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


CASES = (
    (
        "01_macro_keyboard",
        ROOT / "workspace/exercises/01_macro_keyboard/host/hidcheck.py",
        0xC003,
        "UIAP Macro Keyboard",
        "TEST3-001",
        None,
    ),
    (
        "02_rotary_cursor_size",
        ROOT / "workspace/exercises/02_rotary_cursor_size/host/cursor_size_host.py",
        0xC004,
        "UIAP Rotary Cursor",
        "TEST7-001",
        "hidcheck",
    ),
    (
        "03_vibration_motor_console",
        ROOT / "workspace/exercises/03_vibration_motor_console/host/motorctl.py",
        0xC006,
        "UIAP Vibration Console",
        "TEST9-001",
        "hidcheck",
    ),
    (
        "04_rotary_cursor_haptic",
        ROOT / "workspace/exercises/04_rotary_cursor_haptic/host/cursor_size_host.py",
        0xC005,
        "UIAP Rotary Haptic",
        "TEST8-001",
        "hidcheck",
    ),
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(f"test_{name}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class HidcheckContractTests(unittest.TestCase):
    def test_host_product_matches_usb_descriptor(self) -> None:
        for case in CASES:
            with self.subTest(exercise=case[0]):
                descriptor = (
                    ROOT / "workspace" / "exercises" / case[0] / "usb_config.h"
                ).read_text(encoding="utf-8")
                self.assertRegex(
                    descriptor,
                    rf'#define\s+STR_PRODUCT\s+u"{re.escape(case[3])}"',
                )

    def run_hidcheck(self, case, actual_product: str):
        name, path, pid, expected_product, serial, command = case
        module = load_module(name, path)
        device = {
            "vendor_id": 0x1209,
            "product_id": pid,
            "product_string": actual_product,
            "serial_number": serial,
        }
        stdout = StringIO()
        stderr = StringIO()
        argv = [str(path)] + ([command] if command else [])
        with redirect_stdout(stdout), redirect_stderr(stderr), patch.object(
            sys, "argv", argv
        ):
            if name == "01_macro_keyboard":
                fake_hid = SimpleNamespace(enumerate=lambda vid, product_id: [device])
                with patch.dict(sys.modules, {"hid": fake_hid}):
                    result = module.main()
            else:
                module.enumerate_devices = lambda: [device]
                result = module.main()
        return result, stdout.getvalue(), stderr.getvalue(), expected_product

    def test_success_output_is_identical_in_structure(self) -> None:
        for case in CASES:
            with self.subTest(exercise=case[0]):
                result, stdout, stderr, product = self.run_hidcheck(case, case[3])
                self.assertEqual(0, result)
                self.assertEqual("", stderr)
                self.assertEqual(
                    "\n".join(
                        (
                            "Matching devices: 1",
                            f"[0] VID:PID=1209:{case[2]:04X}",
                            f"  Product: {product}",
                            f"  Serial: {case[4]}",
                            f"{product} HID enumeration: PASS",
                            "",
                        )
                    ),
                    stdout,
                )

    def test_product_mismatch_fails(self) -> None:
        for case in CASES:
            with self.subTest(exercise=case[0]):
                result, stdout, stderr, product = self.run_hidcheck(
                    case, "Unexpected Product"
                )
                self.assertNotEqual(0, result)
                self.assertIn(f"Product: Unexpected Product", stdout)
                self.assertIn(f"Expected Product '{product}'", stderr)
                self.assertNotIn("HID enumeration: PASS", stdout)


if __name__ == "__main__":
    unittest.main()
