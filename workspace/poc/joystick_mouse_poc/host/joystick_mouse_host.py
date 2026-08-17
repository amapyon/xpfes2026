#!/usr/bin/env python3
"""PART-03 joystick PoC host application for Windows and macOS."""

from __future__ import annotations

import argparse
import ctypes
import importlib.util
import os
from pathlib import Path
import sys

# TEST-ONLY USB IDENTIFIER
# 1209:0001 is shared, not globally unique, and limited to educational
# prototyping and testing within this workshop. Do not use it for products,
# manufacturing, sale, or redistribution.
VID = 0x1209
PID = 0x0001
PRODUCT = "UIAP Joystick Mouse"
REPORT_SIZE = 4
SPEED_PIXELS = (0, 1, 2, 4, 7, 11)
WINDOWS_LARGE_STEP = 48
MAC_LARGE_STEP = 0.75


def load_cursor_support():
    # UIAP_DEVKIT_ROOT and UIAP_WORKSPACE can both point to the installed
    # Devkit while this PoC lives in a separate source checkout. Prefer the
    # workspace that contains this script, then try the environment value.
    workspace_value = os.environ.get("UIAP_WORKSPACE")
    workspaces = [Path(__file__).resolve().parents[3]]
    if workspace_value:
        environment_workspace = Path(workspace_value).resolve()
        if environment_workspace not in workspaces:
            workspaces.append(environment_workspace)

    sources = [
        workspace
        / "exercises"
        / "02_rotary_cursor_size"
        / "host"
        / "cursor_size_host.py"
        for workspace in workspaces
    ]
    source = next((candidate for candidate in sources if candidate.is_file()), None)
    if source is None:
        searched = "\n  ".join(str(candidate) for candidate in sources)
        raise RuntimeError(f"Cursor support was not found. Searched:\n  {searched}")
    spec = importlib.util.spec_from_file_location("uiap_cursor_support", source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load cursor support: {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.VID = VID
    module.PID = PID
    module.PRODUCT = PRODUCT
    return module


def signed_byte(value: int) -> int:
    value &= 0xFF
    return value - 256 if value >= 128 else value


def decode_report(data: list[int]) -> tuple[int, int, bool] | None:
    if len(data) < REPORT_SIZE:
        return None
    x_level = signed_byte(int(data[0]))
    y_level = signed_byte(int(data[1]))
    if not (-5 <= x_level <= 5 and -5 <= y_level <= 5):
        return None
    return x_level, y_level, bool(data[2])


def speed(level: int) -> int:
    direction = -1 if level < 0 else 1
    return direction * SPEED_PIXELS[min(5, abs(level))]


class WindowsPointer:
    class Point(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

    def __init__(self) -> None:
        self.user32 = ctypes.WinDLL("user32", use_last_error=True)

    def move(self, dx: int, dy: int) -> None:
        point = self.Point()
        if not self.user32.GetCursorPos(ctypes.byref(point)):
            raise ctypes.WinError(ctypes.get_last_error())
        if not self.user32.SetCursorPos(point.x + dx, point.y + dy):
            raise ctypes.WinError(ctypes.get_last_error())


class MacPointer:
    class Point(ctypes.Structure):
        _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]

    def __init__(self) -> None:
        path = "/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics"
        self.cg = ctypes.CDLL(path)
        self.cg.CGEventCreate.argtypes = [ctypes.c_void_p]
        self.cg.CGEventCreate.restype = ctypes.c_void_p
        self.cg.CGEventGetLocation.argtypes = [ctypes.c_void_p]
        self.cg.CGEventGetLocation.restype = self.Point
        self.cg.CGEventPost.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
        self.cg.CGEventPost.restype = None
        self.cg.CGEventCreateMouseEvent.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            self.Point,
            ctypes.c_uint32,
        ]
        self.cg.CGEventCreateMouseEvent.restype = ctypes.c_void_p
        self.cf = ctypes.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
        self.cf.CFRelease.argtypes = [ctypes.c_void_p]

    def move(self, dx: int, dy: int) -> None:
        current_event = self.cg.CGEventCreate(None)
        if not current_event:
            raise RuntimeError("CGEventCreate failed")
        point = self.cg.CGEventGetLocation(current_event)
        self.cf.CFRelease(current_event)
        point.x += dx
        point.y += dy
        move_event = self.cg.CGEventCreateMouseEvent(None, 5, point, 0)
        if not move_event:
            raise RuntimeError("CGEventCreateMouseEvent failed")
        self.cg.CGEventPost(0, move_event)
        self.cf.CFRelease(move_event)


def pointer_backend():
    if sys.platform == "win32":
        return WindowsPointer()
    if sys.platform == "darwin":
        return MacPointer()
    raise RuntimeError(f"Unsupported platform: {sys.platform}")


def enlarged_value(cursor, original):
    current = cursor.current_from_snapshot(original)
    step = WINDOWS_LARGE_STEP if sys.platform == "win32" else MAC_LARGE_STEP
    return cursor.clamp(current + step)


def run(dry_run: bool) -> int:
    support = load_cursor_support()
    device = support.open_device()
    cursor = None if dry_run else support.create_backend()
    pointer = None if dry_run else pointer_backend()
    original = None
    pressed = False
    last_dry_report = None
    try:
        if cursor is not None:
            support.recover_stale_state(cursor)
            original = cursor.snapshot()
            cursor.save_snapshot(original)
        print("Mode: dry-run" if dry_run else "Mode: apply")
        print("Move the joystick. Press Ctrl+C to stop.")
        while True:
            decoded = decode_report(device.read(64, 100))
            if decoded is None:
                continue
            x_level, y_level, new_pressed = decoded
            if dry_run:
                if decoded != last_dry_report:
                    print(f"x={x_level:+d} y={y_level:+d} pressed={int(new_pressed)}", flush=True)
                    last_dry_report = decoded
                continue
            assert cursor is not None and pointer is not None and original is not None
            dx = speed(x_level)
            dy = speed(y_level)
            if dx or dy:
                pointer.move(dx, dy)
            if new_pressed != pressed:
                if new_pressed:
                    cursor.apply(enlarged_value(cursor, original))
                else:
                    cursor.restore_snapshot(original)
                pressed = new_pressed
    except KeyboardInterrupt:
        print("Stopping.")
    finally:
        try:
            device.close()
        except Exception:
            pass
        if cursor is not None and original is not None:
            cursor.restore_snapshot(original)
            cursor.clear_snapshot()
            print("Restored the original pointer size.")
    return 0


def self_test() -> int:
    cases = [
        ([0, 0, 0, 1], (0, 0, False)),
        ([5, 251, 1, 2], (5, -5, True)),
        ([250, 0, 0, 0], None),
        ([], None),
    ]
    for raw, expected in cases:
        actual = decode_report(raw)
        if actual != expected:
            raise RuntimeError(f"decode test failed: {raw} -> {actual}")
    if [speed(i) for i in range(6)] != [0, 1, 2, 4, 7, 11]:
        raise RuntimeError("speed mapping test failed")
    print("report decoder and five-stage speed mapping: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["hidcheck", "app", "dry-run", "self-test", "restore"])
    args = parser.parse_args()
    try:
        support = load_cursor_support()
        if args.command == "hidcheck":
            support.require_one_device()
            print(f"{PRODUCT} HID enumeration: PASS")
            return 0
        if args.command == "self-test":
            return self_test()
        if args.command == "restore":
            return support.restore_saved_state(support.create_backend())
        return run(args.command == "dry-run")
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
