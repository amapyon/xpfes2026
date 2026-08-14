#!/usr/bin/env python3
"""UIAPduino赤外線送信PoCをPCから操作する。"""

from __future__ import annotations

import argparse
import platform
import sys
import time
from typing import Any

VID = 0x1209
PID = 0xD00A
PRODUCT = "UIAP IR Sender PoC"
REPORT_ID = 0x01
REPORT_SIZE = 14
CMD_SEND_TOSHIBA = 1

# ir_recv_pocで実機受信済み。byte 5のMode=1がON、Mode=7がOFF。
TOSHIBA_ON = bytes.fromhex("F20D03FC0190010090")
TOSHIBA_OFF = bytes.fromhex("F20D03FC0190070096")

STATUS = {
    0: "idle",
    1: "sent",
    2: "bad-command",
    3: "bad-frame",
}


def _import_hid() -> Any:
    try:
        import hid
    except Exception as exc:
        raise RuntimeError(
            "hidapiを読み込めません。UIAP Devkitの同梱Pythonを使用してください。"
        ) from exc
    return hid


def enumerate_devices() -> list[dict[str, Any]]:
    devices = list(_import_hid().enumerate(VID, PID))
    exact = [d for d in devices if d.get("product_string") == PRODUCT]
    return exact if exact else devices


def print_devices() -> int:
    devices = enumerate_devices()
    print(f"Matching devices: {len(devices)}")
    for index, device in enumerate(devices):
        print(f"[{index}] VID:PID={VID:04X}:{PID:04X}")
        print(f"  Product: {device.get('product_string') or '(unknown)'}")
        print(f"  Serial: {device.get('serial_number') or '(unknown)'}")
    return 0 if devices else 1


def open_device() -> Any:
    hid = _import_hid()
    devices = enumerate_devices()
    if len(devices) != 1:
        visible = []
        for device in hid.enumerate():
            if int(device.get("vendor_id") or 0) != VID:
                continue
            visible.append(
                f"{int(device.get('vendor_id') or VID):04X}:"
                f"{int(device.get('product_id') or 0):04X} "
                f"{device.get('product_string') or '(unknown)'}"
            )
        suffix = f" 見えているUIAP機器: {', '.join(visible)}" if visible else ""
        raise RuntimeError(
            f"{PRODUCT}を1台だけ接続してください（検出: {len(devices)}台）。{suffix}"
        )
    path = devices[0].get("path")
    if path is None:
        raise RuntimeError("HIDデバイスのパスを取得できません。")
    if hasattr(hid, "device"):
        dev = hid.device()
        dev.open_path(path)
        return dev
    if hasattr(hid, "Device"):
        return hid.Device(path=path)
    raise RuntimeError("未対応のPython hidapi APIです。")


def validate_frame(frame: bytes) -> bytes:
    if len(frame) not in (7, 9, 10):
        raise ValueError("東芝フレームは7、9、10byteのいずれかです。")
    if frame[0] ^ frame[1] != 0xFF or frame[2] ^ frame[3] != 0xFF:
        raise ValueError("先頭の反転byteペアが不正です。")
    if (frame[2] & 0x0F) + 6 != len(frame):
        raise ValueError("フレーム内の長さと実データ長が一致しません。")
    checksum = 0
    for value in frame[:-1]:
        checksum ^= value
    if checksum != frame[-1]:
        raise ValueError(
            f"XORチェックサムが不正です（期待値: {checksum:02X}）。"
        )
    return frame


def parse_hex_frame(text: str) -> bytes:
    compact = text.replace("0x", "").replace("0X", "")
    compact = "".join(compact.replace(",", " ").split())
    try:
        frame = bytes.fromhex(compact)
    except ValueError as exc:
        raise ValueError("コードは16進数で指定してください。") from exc
    return validate_frame(frame)


def encode_report(frame: bytes, count: int = 2) -> bytes:
    validate_frame(frame)
    if not 1 <= count <= 4:
        raise ValueError("送信回数は1～4で指定してください。")
    return bytes((REPORT_ID, CMD_SEND_TOSHIBA, len(frame), count)) + frame.ljust(10, b"\0")


def send_frame(frame: bytes, count: int = 2) -> None:
    report = encode_report(frame, count)
    dev = open_device()
    try:
        result = dev.send_feature_report(report)
        if result is not None and result < 0:
            raise RuntimeError("Feature Reportの送信に失敗しました。")
    finally:
        dev.close()
    print(f"送信要求: 0x{frame.hex().upper()} x {count}")


def get_status() -> tuple[int, int, int]:
    dev = open_device()
    try:
        data = list(dev.get_feature_report(REPORT_ID, REPORT_SIZE))
    finally:
        dev.close()
    if not data:
        raise RuntimeError("Feature Reportの取得に失敗しました。")
    offset = 1 if data[0] == REPORT_ID else 0
    if len(data) - offset < 3:
        raise RuntimeError("状態レポートが短すぎます。")
    return int(data[offset]), int(data[offset + 1]), int(data[offset + 2])


def wait_for_result(timeout: float = 2.0) -> tuple[int, int, int]:
    deadline = time.monotonic() + timeout
    result = (0, 0, 0)
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            result = get_status()
            last_error = None
        except (OSError, RuntimeError) as exc:
            # IR timing is protected by masking USB for roughly 200ms.
            # Windows hidapi can report a transient read error in that window.
            last_error = exc
            time.sleep(0.05)
            continue
        if result[0] != 0:
            return result
        time.sleep(0.05)
    if last_error is not None:
        raise RuntimeError(
            f"送信完了後も状態を読み取れませんでした: {last_error}"
        ) from last_error
    return result


def print_status(result: tuple[int, int, int]) -> int:
    status, length, count = result
    print(f"device: {STATUS.get(status, f'unknown-{status}')} length={length} count={count}")
    return 0 if status in (0, 1) else 1


def self_test() -> int:
    assert validate_frame(TOSHIBA_ON) == TOSHIBA_ON
    assert validate_frame(TOSHIBA_OFF) == TOSHIBA_OFF
    assert parse_hex_frame("0xF20D03FC0190010090") == TOSHIBA_ON
    assert parse_hex_frame("F2 0D 03 FC 01 90 07 00 96") == TOSHIBA_OFF
    report = encode_report(TOSHIBA_ON, 2)
    assert len(report) == REPORT_SIZE
    assert report[:4] == bytes((1, 1, 9, 2))
    for invalid in ("", "F20D", "F20D03FC0190010091"):
        try:
            parse_hex_frame(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid frame accepted: {invalid!r}")
    print("ir_send_host self-test: PASS")
    return 0


def doctor() -> int:
    self_test()
    hid = _import_hid()
    print(f"Host platform: {sys.platform} / {platform.machine() or 'unknown'}")
    print(f"Python: {platform.python_version()}")
    print(f"hidapi import: PASS ({getattr(hid, '__version__', 'unknown')})")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--doctor", action="store_true")
    parser.add_argument("--list", action="store_true")
    sub = parser.add_subparsers(dest="command")
    on = sub.add_parser("on", help="実機受信済みのONフレームを送信")
    on.add_argument("--count", type=int, default=2)
    off = sub.add_parser("off", help="実機受信済みのOFFフレームを送信")
    off.add_argument("--count", type=int, default=2)
    raw = sub.add_parser("raw", help="任意の東芝フレームを送信")
    raw.add_argument("code")
    raw.add_argument("--count", type=int, default=2)
    sub.add_parser("status", help="最後のデバイス処理結果を表示")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.self_test:
            return self_test()
        if args.doctor:
            return doctor()
        if args.list:
            return print_devices()
        if args.command == "on":
            send_frame(TOSHIBA_ON, args.count)
            return print_status(wait_for_result())
        if args.command == "off":
            send_frame(TOSHIBA_OFF, args.count)
            return print_status(wait_for_result())
        if args.command == "raw":
            send_frame(parse_hex_frame(args.code), args.count)
            return print_status(wait_for_result())
        if args.command == "status":
            return print_status(get_status())
        build_parser().print_help()
        return 2
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
