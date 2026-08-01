#!/usr/bin/env python3
"""macOS host application for XP祭り2026 02_rotary_cursor_size.

HID transport uses hidapi. Cursor-size control uses unsupported private
CoreGraphics/SkyLight symbols via ctypes and therefore requires real-machine
validation on each supported macOS line.
"""
from __future__ import annotations

# macOS-specific pointer-size host for the shared encoder HID firmware.

import ctypes
import math
import os
from pathlib import Path
import struct
import sys
from typing import Any

try:
    import hid
except Exception as exc:
    print(f"[UIAP-CURSOR-E203] Could not import bundled hidapi: {exc}", file=sys.stderr)
    raise SystemExit(203)

VERSION = "0.2.2-test13"
VID = 0x1209
PID = 0xC004
CURSOR_STEP = 0.25
CURSOR_MIN = 0.50
CURSOR_MAX = 4.00
OBSERVED_MIN = 0.25
OBSERVED_MAX = 16.00
COMPARE_TOLERANCE = 0.02
PROBE_BITS = 0x7FF8000000000000
PROBE_HIGH_WORD = 0x7FF80000


def observable(value: float) -> bool:
    return math.isfinite(value) and OBSERVED_MIN <= value <= OBSERVED_MAX


def close_enough(a: float, b: float) -> bool:
    return abs(a - b) <= COMPARE_TOLERANCE


def clamp(value: float) -> float:
    return max(CURSOR_MIN, min(CURSOR_MAX, value))


def _symbol_address(libraries: list[ctypes.CDLL], name: str) -> int | None:
    for lib in libraries:
        try:
            fn = getattr(lib, name)
        except AttributeError:
            continue
        address = ctypes.cast(fn, ctypes.c_void_p).value
        if address:
            return int(address)
    return None


class CursorAPI:
    def __init__(self) -> None:
        self.libs: list[ctypes.CDLL] = []
        for path in (
            "/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics",
            "/System/Library/PrivateFrameworks/SkyLight.framework/SkyLight",
        ):
            try:
                self.libs.append(ctypes.CDLL(path))
            except OSError:
                pass
        try:
            self.libs.append(ctypes.CDLL(None))
        except OSError:
            pass

        main_addr = _symbol_address(self.libs, "CGSMainConnectionID")
        get_addr = _symbol_address(self.libs, "CGSGetCursorScale")
        set_addr = _symbol_address(self.libs, "CGSSetCursorScale")
        if not (main_addr and get_addr and set_addr):
            raise RuntimeError("private cursor-scale symbols are unavailable")

        self._main = ctypes.CFUNCTYPE(ctypes.c_int32)(main_addr)
        self._get_raw = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.c_int32, ctypes.c_void_p)(get_addr)
        self._set_float = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.c_int32, ctypes.c_float)(set_addr)
        self._set_double = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.c_int32, ctypes.c_double)(set_addr)
        self.abi: str | None = None

    @property
    def connection(self) -> int:
        return int(self._main())

    def _detect_abi(self) -> float:
        probe = ctypes.create_string_buffer(struct.pack("<Q", PROBE_BITS), 8)
        result = self._get_raw(self.connection, ctypes.cast(probe, ctypes.c_void_p))
        if result != 0:
            raise RuntimeError(f"CGSGetCursorScale returned {result}")
        raw = bytes(probe.raw[:8])
        float_value = float(struct.unpack("<f", raw[:4])[0])
        high_word = struct.unpack("<I", raw[4:8])[0]
        double_value = float(struct.unpack("<d", raw)[0])
        if high_word == PROBE_HIGH_WORD and observable(float_value):
            self.abi = "float32"
            return float_value
        if observable(double_value):
            self.abi = "float64"
            return double_value
        if observable(float_value):
            self.abi = "float32"
            return float_value
        raise RuntimeError("cursor-scale ABI probe returned no observable value")

    def get(self) -> float:
        if self.abi is None:
            return self._detect_abi()
        if self.abi == "float32":
            value = ctypes.c_float(float("nan"))
        else:
            value = ctypes.c_double(float("nan"))
        result = self._get_raw(self.connection, ctypes.cast(ctypes.byref(value), ctypes.c_void_p))
        current = float(value.value)
        if result != 0 or not observable(current):
            raise RuntimeError(f"cursor-scale read failed result={result} value={current!r}")
        return current

    def set(self, value: float) -> None:
        if self.abi is None:
            self.get()
        if not observable(value):
            raise RuntimeError(f"refusing invalid pointer scale {value!r}")
        result = self._set_float(self.connection, value) if self.abi == "float32" else self._set_double(self.connection, value)
        if result != 0:
            raise RuntimeError(f"CGSSetCursorScale returned {result}")

    def self_test(self) -> float:
        before = self.get()
        self.set(before)
        after = self.get()
        if not close_enough(before, after):
            raise RuntimeError(f"no-op write/readback mismatch: before={before:.6g} after={after:.6g}")
        return after


def state_path() -> Path:
    root = os.environ.get("UIAP_DEVKIT_ROOT")
    if not root:
        raise RuntimeError("UIAP_DEVKIT_ROOT is not set")
    return Path(root) / ".state" / "02_rotary_cursor_size.original-scale"


def remove_saved_scale() -> None:
    try:
        state_path().unlink(missing_ok=True)
    except OSError:
        pass


def read_saved_scale() -> float:
    path = state_path()
    try:
        value = float(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError) as exc:
        raise RuntimeError("no valid saved pointer size is available") from exc
    if not observable(value):
        raise RuntimeError("saved pointer size is outside the observable range")
    return value


def save_original_scale(value: float) -> None:
    if not observable(value):
        raise RuntimeError("refusing to save an invalid pointer size")
    path = state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{value:.9g}\n", encoding="utf-8")
    os.chmod(path, 0o600)


def restore_saved(api: CursorAPI) -> bool:
    try:
        original = read_saved_scale()
    except RuntimeError:
        remove_saved_scale()
        print("[UIAP-CURSOR-E205] No valid saved pointer size is available.", file=sys.stderr)
        return False
    try:
        api.set(original)
        restored = api.get()
    except RuntimeError as exc:
        print(f"[UIAP-CURSOR-E206] Could not restore pointer size {original:.2f}: {exc}", file=sys.stderr)
        return False
    if not close_enough(original, restored):
        print(f"[UIAP-CURSOR-E209] Pointer-size restore verification failed; expected {original:.2f}.", file=sys.stderr)
        return False
    remove_saved_scale()
    print(f"Restored pointer scale: {restored:.2f}")
    return True


def matching_devices() -> list[dict[str, Any]]:
    try:
        devices = list(hid.enumerate(VID, PID))
    except Exception as exc:
        print(f"[UIAP-CURSOR-E204] hidapi enumeration failed: {exc}", file=sys.stderr)
        return []
    return devices


def print_devices(devices: list[dict[str, Any]]) -> None:
    print(f"Matching devices: {len(devices)}")
    for index, info in enumerate(devices):
        print(f"[{index}] VID:PID={VID:04X}:{PID:04X}")
        product = info.get("product_string")
        serial = info.get("serial_number")
        if product:
            print(f"  Product: {product}")
        if serial:
            print(f"  Serial: {serial}")


def open_single_device() -> Any:
    devices = matching_devices()
    print_devices(devices)
    if len(devices) != 1:
        raise RuntimeError(f"connect exactly one 1209:C004 device; detected {len(devices)}")
    path = devices[0].get("path")
    if path is None:
        raise RuntimeError("hidapi did not return a device path")
    dev = hid.device()
    try:
        dev.open_path(path)
    except Exception:
        try:
            dev.close()
        except Exception:
            pass
        raise
    return dev


def read_delta(dev: Any) -> int | None:
    data = dev.read(64, 100)
    if not data:
        return None
    value = int(data[0]) & 0xFF
    return value - 256 if value >= 128 else value


def run_hid(dry_run: bool) -> int:
    api: CursorAPI | None = None
    current = float("nan")
    should_restore = False
    if not dry_run:
        try:
            api = CursorAPI()
            current = api.self_test()
        except Exception as exc:
            print(f"[UIAP-CURSOR-E214] Cursor-scale ABI/read/write self-test failed: {exc}", file=sys.stderr)
            return 214
        try:
            original = read_saved_scale()
        except RuntimeError:
            remove_saved_scale()
            original = current
            try:
                save_original_scale(original)
            except Exception as exc:
                print(f"[UIAP-CURSOR-E208] Could not save the original pointer size: {exc}", file=sys.stderr)
                return 208
        should_restore = True
        print(f"Cursor-scale ABI: {api.abi}")
        print(f"Original pointer scale: {original:.2f}")
        print(f"Current pointer scale: {current:.2f}")

    try:
        dev = open_single_device()
    except Exception as exc:
        print(f"[UIAP-CURSOR-E210] Could not open exactly one HID device: {exc}", file=sys.stderr)
        if should_restore and api is not None:
            restore_saved(api)
        return 210

    status = 0
    print(f"Mode: {'dry-run' if dry_run else 'pointer-size control'}")
    print("Rotate the encoder. Press Ctrl+C to stop.")
    try:
        while True:
            delta = read_delta(dev)
            if not delta:
                continue
            direction = "CW" if delta > 0 else "CCW"
            if dry_run:
                print(f"{direction} delta={delta}", flush=True)
                continue
            assert api is not None
            target = clamp(current + delta * CURSOR_STEP)
            if close_enough(target, current):
                print(f"{direction} limit scale={current:.2f}", flush=True)
                continue
            try:
                api.set(target)
                applied = api.get()
            except Exception as exc:
                print(f"[UIAP-CURSOR-E207] Could not set pointer scale {target:.2f}: {exc}", file=sys.stderr)
                status = 207
                break
            if not close_enough(target, applied):
                print(f"[UIAP-CURSOR-E216] Pointer-scale write verification failed; requested {target:.2f}.", file=sys.stderr)
                status = 216
                break
            current = applied
            print(f"{direction} scale={applied:.2f}", flush=True)
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        print(f"[UIAP-CURSOR-E212] HID device was disconnected or read failed: {exc}", file=sys.stderr)
        status = 212
    finally:
        try:
            dev.close()
        except Exception:
            pass
        if should_restore and api is not None and not restore_saved(api) and status == 0:
            status = 206
    return status


def self_test() -> int:
    try:
        api = CursorAPI()
        scale = api.self_test()
    except Exception as exc:
        print(f"[UIAP-CURSOR-E214] Cursor-scale ABI/read/write self-test failed: {exc}", file=sys.stderr)
        return 214
    print(f"Cursor-scale API: PASS abi={api.abi} current={scale:.2f} no-op-write=PASS")
    return 0


def restore_mode() -> int:
    try:
        api = CursorAPI()
        api.get()
    except Exception as exc:
        print(f"[UIAP-CURSOR-E201] Private cursor-scale API is unavailable: {exc}", file=sys.stderr)
        return 201
    return 0 if restore_saved(api) else 205


def usage() -> None:
    print("Usage: cursor_size_host.py [--list|--dry-run|--restore|--self-test|--version]")


def main(argv: list[str]) -> int:
    if len(argv) > 2:
        usage()
        return 64
    mode = argv[1] if len(argv) == 2 else "--run"
    if mode == "--version":
        print(f"uiap-cursor-host.py {VERSION} macarm64 python")
        return 0
    if mode == "--list":
        print_devices(matching_devices())
        return 0
    if mode == "--self-test":
        return self_test()
    if mode == "--restore":
        return restore_mode()
    if mode == "--dry-run":
        return run_hid(True)
    if mode == "--run":
        return run_hid(False)
    usage()
    return 64


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
