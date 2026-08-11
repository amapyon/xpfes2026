#!/usr/bin/env python3
"""03_vibration_motor_console用のWindows/macOS共通ホスト。"""

from __future__ import annotations

import argparse
import platform
import sys
import time
from typing import Any

VID = 0x1209
PID = 0xC006
PRODUCT = "UIAP Vibration Console"
REPORT_ID = 0x01
VERSION = "0.2.0"


def _import_hid() -> Any:
    try:
        import hid
    except Exception as exc:
        raise RuntimeError(
            "hidapiを読み込めません。UIAP Devkitの同梱Pythonから実行してください。"
        ) from exc
    return hid


def matching_devices(hid_module: Any) -> list[dict[str, Any]]:
    """VID/PIDに一致し、可能ならProduct文字列も一致するデバイスを返す。"""
    devices = list(hid_module.enumerate(VID, PID))
    exact = [device for device in devices if device.get("product_string") == PRODUCT]
    return exact if exact else devices


def print_devices() -> int:
    devices = matching_devices(_import_hid())
    print(f"Matching devices: {len(devices)}")
    for index, device in enumerate(devices):
        print(f"[{index}] VID:PID={VID:04X}:{PID:04X}")
        print(f"  Product: {device.get('product_string')}")
        print(f"  Serial: {device.get('serial_number')}")
        print(f"  Path: {device.get('path')}")
    return 0 if devices else 1


def open_device() -> Any:
    hid = _import_hid()
    devices = matching_devices(hid)
    if not devices:
        raise RuntimeError(f"{PRODUCT} ({VID:04X}:{PID:04X}) が見つかりません。")
    if len(devices) != 1:
        raise RuntimeError(f"対象デバイスが{len(devices)}台あります。1台だけ接続してください。")
    path = devices[0].get("path")
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


def set_level(level: int) -> None:
    """Feature Report ID 1で振動レベル0〜100を送る。"""
    level = validate_level(level)
    dev = open_device()
    try:
        result = dev.send_feature_report(bytes((REPORT_ID, level)))
        if result is not None and result < 0:
            raise RuntimeError("Feature Reportの送信に失敗しました。")
    finally:
        dev.close()


def get_level() -> int:
    dev = open_device()
    try:
        data = dev.get_feature_report(REPORT_ID, 2)
    finally:
        dev.close()
    if not data:
        raise RuntimeError("Feature Reportの取得に失敗しました。")
    value = data[1] if len(data) >= 2 and data[0] == REPORT_ID else data[-1]
    return validate_level(int(value))


def validate_pulse_seconds(seconds: float) -> float:
    if not 0.01 <= seconds <= 5.0:
        raise ValueError("秒数は0.01以上5.0以下で指定してください。")
    return seconds


def pulse(level: int, seconds: float) -> None:
    level = validate_level(level)
    if level == 0:
        raise ValueError("pulseの振動レベルは1以上100以下で指定してください。")
    seconds = validate_pulse_seconds(seconds)
    set_level(level)
    try:
        time.sleep(seconds)
    finally:
        set_level(0)


def self_test() -> int:
    assert bytes((REPORT_ID, 75)) == b"\x01\x4b"
    assert bytes((REPORT_ID, 0)) == b"\x01\x00"
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("self-test")
    sub.add_parser("doctor")
    sub.add_parser("list")
    on_parser = sub.add_parser("on")
    on_parser.add_argument("level", nargs="?", type=int, default=50)
    sub.add_parser("off")
    sub.add_parser("status")
    pulse_parser = sub.add_parser("pulse")
    pulse_parser.add_argument("seconds", nargs="?", type=float, default=0.2)
    pulse_parser.add_argument("level", nargs="?", type=int, default=50)
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
        if args.command == "list":
            return print_devices()
        if args.command == "on":
            level = validate_level(args.level)
            if level == 0:
                raise ValueError("onの振動レベルは1以上100以下で指定してください。")
            set_level(level)
            print(f"motor: on (level {level})")
            return 0
        if args.command == "off":
            set_level(0)
            print("motor: off")
            return 0
        if args.command == "status":
            level = get_level()
            print("motor: off" if level == 0 else f"motor: on (level {level})")
            return 0
        if args.command == "pulse":
            pulse(args.level, args.seconds)
            print(
                f"motor: pulse (level {args.level}, "
                f"{args.seconds:g} seconds), then off"
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
