#!/usr/bin/env python3
"""Host controller for the UIAP vibration motor HID PoC."""

from __future__ import annotations

import argparse
import math
import platform
import signal
import sys
import time

# TEST-ONLY USB IDENTIFIER
# 1209:0001 is shared, not globally unique, and limited to educational
# prototyping and testing within this workshop. Do not use it for products,
# manufacturing, sale, or redistribution.
VID = 0x1209
PID = 0x0001
PRODUCT = "UIAP Vibration Motor"
REPORT_ID = 0x01

_stop = False


def _signal_stop(signum, frame):
    del signum, frame
    global _stop
    _stop = True


def _import_hid():
    try:
        import hid
    except Exception as exc:
        raise RuntimeError(
            "hidapiを読み込めません。UIAP Devkitの同梱Pythonから実行してください。"
        ) from exc
    return hid


def matching_devices(hid_module):
    devices = list(hid_module.enumerate(VID, PID))
    exact = [device for device in devices if device.get("product_string") == PRODUCT]
    return exact if exact else devices


def print_devices() -> int:
    hid_module = _import_hid()
    devices = matching_devices(hid_module)
    print(f"Matching devices: {len(devices)}")
    for index, device in enumerate(devices):
        print(f"[{index}] VID:PID={VID:04X}:{PID:04X}")
        print(f"  Product: {device.get('product_string')}")
        print(f"  Serial: {device.get('serial_number')}")
        print(f"  Path: {device.get('path')}")
    return 0 if devices else 1


def open_device():
    hid = _import_hid()
    devices = matching_devices(hid)
    if not devices:
        raise RuntimeError(f"{PRODUCT} ({VID:04X}:{PID:04X}) が見つかりません。")
    if len(devices) != 1:
        raise RuntimeError(
            f"対象デバイスが{len(devices)}台あります。1台だけ接続してください。"
        )

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


def set_level(level: int):
    if not 0 <= level <= 100:
        raise ValueError("level must be in the range 0..100")

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

    if len(data) >= 2 and data[0] == REPORT_ID:
        return int(data[1])

    # Some backends return only the payload byte.
    return int(data[-1])


def parse_pattern(text: str):
    steps = []
    for raw in text.split(","):
        part = raw.strip()
        if not part:
            raise ValueError("empty pattern step")

        if ":" not in part:
            raise ValueError(f"':' がありません: {part}")

        level_text, seconds_text = (x.strip() for x in part.split(":", 1))

        try:
            level = int(level_text, 10)
        except ValueError as exc:
            raise ValueError(f"levelが整数ではありません: {level_text}") from exc

        try:
            seconds = float(seconds_text)
        except ValueError as exc:
            raise ValueError(f"秒数が数値ではありません: {seconds_text}") from exc

        if not 0 <= level <= 100:
            raise ValueError(f"levelは0..100で指定してください: {level}")

        if not math.isfinite(seconds) or seconds <= 0 or seconds > 3600:
            raise ValueError(f"秒数は0より大きく3600以下にしてください: {seconds}")

        steps.append((level, seconds))

    if not steps:
        raise ValueError("pattern is empty")
    if len(steps) > 32:
        raise ValueError("pattern steps must be 32 or fewer")

    return steps


def self_test() -> int:
    assert parse_pattern("100:0.1, 0:0.4") == [(100, 0.1), (0, 0.4)]
    assert parse_pattern("50:1") == [(50, 1.0)]

    invalid = ["", "100", "-1:1", "101:1", "50:0", "50:nan", "1:1,"]
    for pattern in invalid:
        try:
            parse_pattern(pattern)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid pattern accepted: {pattern!r}")

    print("motorctl parser self-test: PASS")
    return 0


def platform_doctor() -> int:
    self_test()
    hid_module = _import_hid()
    machine = platform.machine()
    if sys.platform == "darwin" and machine != "arm64":
        raise RuntimeError(
            f"macOSではApple Silicon arm64版Pythonが必要です: detected {machine or 'unknown'}"
        )
    version = getattr(hid_module, "__version__", "unknown")
    print(f"Host platform: {sys.platform} / {machine or 'unknown'}")
    print(f"Python: {platform.python_version()}")
    print(f"hidapi import: PASS (version {version})")
    return 0


def play(pattern: str):
    global _stop
    _stop = False

    steps = parse_pattern(pattern)
    signal.signal(signal.SIGINT, _signal_stop)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _signal_stop)

    print(f"play: {pattern}")
    print("Ctrl+Cで停止します。")

    try:
        while not _stop:
            for level, seconds in steps:
                if _stop:
                    break
                set_level(level)

                deadline = time.monotonic() + seconds
                while not _stop:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        break
                    time.sleep(min(0.01, remaining))
    finally:
        try:
            set_level(0)
            print("motor: off")
        except Exception as exc:
            print(f"警告: 停止コマンド送信失敗: {exc}", file=sys.stderr)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--doctor", action="store_true")
    parser.add_argument("--list", action="store_true")

    sub = parser.add_subparsers(dest="command")

    on = sub.add_parser("on")
    on.add_argument("level", nargs="?", type=int, default=50)

    sub.add_parser("off")
    sub.add_parser("status")

    p = sub.add_parser("play")
    p.add_argument("pattern", nargs="?", default="100:0.1,0:0.4")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    try:
        if args.doctor:
            return platform_doctor()

        if args.list:
            return print_devices()

        if args.command == "on":
            if not 1 <= args.level <= 100:
                parser.error("level must be an integer from 1 to 100")
            set_level(args.level)
            print(f"motor: on (level {args.level})")
            return 0

        if args.command == "off":
            set_level(0)
            print("motor: off")
            return 0

        if args.command == "status":
            level = get_level()
            if level == 0:
                print("motor: off")
            else:
                print(f"motor: on (level {level})")
            return 0

        if args.command == "play":
            play(args.pattern)
            return 0

        parser.print_help()
        return 2

    except (RuntimeError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
