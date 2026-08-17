#!/usr/bin/env python3
"""03_vibration_motor_console用のWindows/macOS共通ホスト。"""

from __future__ import annotations

import argparse
import platform
import sys
from typing import Any

# TEST-ONLY USB IDENTIFIER
# 1209:0001 is shared, not globally unique, and limited to educational
# prototyping and testing within this workshop. Do not use it for products,
# manufacturing, sale, or redistribution.
VID = 0x1209
PID = 0x0001
PRODUCT = "UIAP Vibration Console"
REPORT_ID = 0x01
REPORT_SIZE = 7
MAX_PATTERN_MS = 5000
VERSION = "0.3.0"


def _import_hid() -> Any:
    try:
        import hid
    except Exception as exc:
        raise RuntimeError(
            "hidapiを読み込めません。UIAP Devkitの同梱Pythonから実行してください。"
        ) from exc
    return hid


def enumerate_devices() -> list[dict[str, Any]]:
    return list(_import_hid().enumerate(VID, PID))


def print_devices(devices: list[dict[str, Any]]) -> None:
    print(f"Matching devices: {len(devices)}")
    for index, device in enumerate(devices):
        print(
            f"[{index}] VID:PID="
            f"{device.get('vendor_id', VID):04X}:"
            f"{device.get('product_id', PID):04X}"
        )
        print(f"  Product: {device.get('product_string') or '(unknown)'}")
        print(f"  Serial: {device.get('serial_number') or '(unknown)'}")


def require_one_device() -> dict[str, Any]:
    devices = enumerate_devices()
    print_devices(devices)
    if len(devices) != 1:
        raise RuntimeError(
            "[UIAP-MOTOR-E201] Connect exactly one UIAP Vibration Console."
        )
    actual_product = devices[0].get("product_string") or "(unknown)"
    if actual_product != PRODUCT:
        raise RuntimeError(
            f"[UIAP-MOTOR-E202] Expected Product '{PRODUCT}', "
            f"got '{actual_product}'."
        )
    return devices[0]


def open_device() -> Any:
    hid = _import_hid()
    info = require_one_device()
    path = info.get("path")
    if path is None:
        raise RuntimeError("HIDデバイスのパスを取得できません。")

    try:
        if hasattr(hid, "device"):
            dev = hid.device()
            dev.open_path(path)
            return dev
        if hasattr(hid, "Device"):
            return hid.Device(path=path)
    except Exception as exc:
        raise RuntimeError("HIDデバイスを開けません。") from exc
    raise RuntimeError("未対応のPython hidapi APIです。")


def validate_level(level: int) -> int:
    if not 0 <= level <= 100:
        raise ValueError("振動レベルは0以上100以下で指定してください。")
    return level


def validate_ms(value: int) -> int:
    if not 0 <= value <= MAX_PATTERN_MS:
        raise ValueError(f"ON/OFF時間は0以上{MAX_PATTERN_MS}ms以下で指定してください。")
    return value


def validate_count(count: int) -> int:
    if not 0 <= count <= 255:
        raise ValueError("回数は0以上255以下で指定してください。")
    return count


def encode_pattern(level: int, on_ms: int, off_ms: int, count: int) -> bytes:
    level = validate_level(level)
    on_ms = validate_ms(on_ms)
    off_ms = validate_ms(off_ms)
    count = validate_count(count)
    if level > 0 and count > 0 and on_ms == 0:
        raise ValueError("有限パターンのON時間は1ms以上で指定してください。")
    return bytes(
        (
            REPORT_ID,
            level,
            on_ms & 0xFF,
            (on_ms >> 8) & 0xFF,
            off_ms & 0xFF,
            (off_ms >> 8) & 0xFF,
            count,
        )
    )


def send_pattern(level: int, on_ms: int, off_ms: int, count: int) -> None:
    """LEVEL、ON/OFF時間、回数を1つのFeature Reportで送る。"""
    report = encode_pattern(level, on_ms, off_ms, count)
    dev = open_device()
    try:
        result = dev.send_feature_report(report)
        if result is not None and result < 0:
            raise RuntimeError("Feature Reportの送信に失敗しました。")
    finally:
        dev.close()


def get_pattern() -> tuple[int, int, int, int]:
    dev = open_device()
    try:
        data = list(dev.get_feature_report(REPORT_ID, REPORT_SIZE))
    finally:
        dev.close()
    if not data:
        raise RuntimeError("Feature Reportの取得に失敗しました。")
    offset = 1 if data[0] == REPORT_ID else 0
    if len(data) - offset < 6:
        raise RuntimeError("Feature Reportの長さが不正です。")
    level = validate_level(int(data[offset]))
    on_ms = int(data[offset + 1]) | (int(data[offset + 2]) << 8)
    off_ms = int(data[offset + 3]) | (int(data[offset + 4]) << 8)
    count = int(data[offset + 5])
    return level, on_ms, off_ms, count


def validate_pulse_seconds(seconds: float) -> float:
    if not 0.01 <= seconds <= 5.0:
        raise ValueError("秒数は0.01以上5.0以下で指定してください。")
    return seconds


def pulse(level: int, seconds: float) -> None:
    level = validate_level(level)
    if level == 0:
        raise ValueError("pulseの振動レベルは1以上100以下で指定してください。")
    seconds = validate_pulse_seconds(seconds)
    send_pattern(level, round(seconds * 1000), 0, 1)


def self_test() -> int:
    assert encode_pattern(75, 80, 40, 2) == b"\x01\x4b\x50\x00\x28\x00\x02"
    assert encode_pattern(0, 0, 0, 0) == b"\x01\x00\x00\x00\x00\x00\x00"
    assert validate_level(1) == 1
    assert validate_level(100) == 100
    for level in (-1, 101):
        try:
            validate_level(level)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid level accepted: {level}")
    assert validate_pulse_seconds(0.2) == 0.2
    assert validate_ms(5000) == 5000
    assert validate_count(255) == 255
    for value in (0.0, 0.009, 5.001):
        try:
            validate_pulse_seconds(value)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid pulse accepted: {value}")
    print("motorctl protocol self-test: PASS")
    return 0


def doctor() -> int:
    self_test()
    hid = _import_hid()
    machine = platform.machine()
    if sys.platform == "darwin" and machine != "arm64":
        raise RuntimeError(f"macOSではApple Silicon arm64版Pythonが必要です: {machine}")
    print(f"Host platform: {sys.platform} / {machine or 'unknown'}")
    print(f"Python: {platform.python_version()}")
    print(f"hidapi import: PASS (version {getattr(hid, '__version__', 'unknown')})")
    return 0


def hidcheck() -> int:
    require_one_device()
    print(f"{PRODUCT} HID enumeration: PASS")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("self-test")
    sub.add_parser("doctor")
    sub.add_parser("hidcheck")
    sub.add_parser("list")
    on_parser = sub.add_parser("on")
    on_parser.add_argument("level", nargs="?", type=int, default=50)
    sub.add_parser("off")
    sub.add_parser("status")
    pulse_parser = sub.add_parser("pulse")
    pulse_parser.add_argument("seconds", nargs="?", type=float, default=0.2)
    pulse_parser.add_argument("level", nargs="?", type=int, default=50)
    pattern_parser = sub.add_parser("pattern")
    pattern_parser.add_argument("level", type=int)
    pattern_parser.add_argument("on_ms", type=int)
    pattern_parser.add_argument("off_ms", type=int)
    pattern_parser.add_argument("count", type=int)
    sub.add_parser("version")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "self-test":
            return self_test()
        if args.command == "doctor":
            return doctor()
        if args.command == "hidcheck":
            return hidcheck()
        if args.command == "list":
            print_devices(enumerate_devices())
            return 0
        if args.command == "on":
            level = validate_level(args.level)
            if level == 0:
                raise ValueError("onの振動レベルは1以上100以下で指定してください。")
            send_pattern(level, 0, 0, 0)
            print(f"motor: on (level {level})")
            return 0
        if args.command == "off":
            send_pattern(0, 0, 0, 0)
            print("motor: off")
            return 0
        if args.command == "status":
            level, on_ms, off_ms, count = get_pattern()
            if level == 0:
                print("motor: off")
            elif count == 0:
                print(f"motor: on (level {level})")
            else:
                print(
                    f"motor: pattern active (level {level}, on {on_ms}ms, "
                    f"off {off_ms}ms, count {count})"
                )
            return 0
        if args.command == "pulse":
            pulse(args.level, args.seconds)
            print(
                f"motor: pulse (level {args.level}, "
                f"{args.seconds:g} seconds), automatic stop"
            )
            return 0
        if args.command == "pattern":
            if args.level == 0:
                raise ValueError("patternの振動レベルは1以上100以下で指定してください。")
            if args.count == 0:
                raise ValueError("patternの回数は1以上255以下で指定してください。")
            send_pattern(args.level, args.on_ms, args.off_ms, args.count)
            print(
                f"motor: pattern (level {args.level}, on {args.on_ms}ms, "
                f"off {args.off_ms}ms, count {args.count}), automatic stop"
            )
            return 0
        if args.command == "version":
            print(f"uiap-motorctl.py {VERSION} {sys.platform} python")
            return 0
        parser.print_help()
        return 2
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
