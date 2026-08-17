#!/usr/bin/env python3
"""PC controller for the UIAPduino PART-09 OLED PoC."""

from __future__ import annotations

import argparse
import platform
import sys
import time
from typing import Any, Sequence

# TEST-ONLY USB IDENTIFIER
# 1209:0001 is shared, not globally unique, and limited to educational
# prototyping and testing within this workshop. Do not use it for products,
# manufacturing, sale, or redistribution.
VID = 0x1209
PID = 0x0001
PRODUCT = "UIAP OLED PoC"
REPORT_ID = 0x01
REPORT_SIZE = 25
TEXT_BYTES_PER_REPORT = 19

COMMANDS = {
    "output": 1,
    "clear": 2,
    "fill": 3,
    "text": 4,
    "line": 5,
    "rect": 6,
    "circle": 7,
    "demo": 8,
    "probe": 9,
}
STATUS = {
    0: "idle",
    1: "ok",
    2: "bad-command",
    3: "bad-argument",
    4: "oled-not-found",
    5: "i2c-error",
}
_sequence = 0


def import_hid() -> Any:
    try:
        import hid
    except Exception as exc:
        raise RuntimeError(
            "hidapiを読み込めません。UIAP Devkitの環境から実行してください。"
        ) from exc
    return hid


def matching_devices() -> list[dict[str, Any]]:
    devices = list(import_hid().enumerate(VID, PID))
    exact = [d for d in devices if d.get("product_string") == PRODUCT]
    return exact if exact else devices


def print_devices() -> int:
    devices = matching_devices()
    print(f"Matching devices: {len(devices)}")
    for index, device in enumerate(devices):
        print(f"[{index}] VID:PID={VID:04X}:{PID:04X}")
        print(f"  Product: {device.get('product_string') or '(unknown)'}")
        print(f"  Serial: {device.get('serial_number') or '(unknown)'}")
    return 0 if devices else 1


def open_device() -> Any:
    hid = import_hid()
    devices = matching_devices()
    if len(devices) != 1:
        raise RuntimeError(
            f"{PRODUCT}を1台だけ接続してください（検出: {len(devices)}台）。"
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


def decode_text(value: str) -> bytes:
    r"""Encode ASCII literally and allow \xNN for arbitrary byte codes."""
    result = bytearray()
    pos = 0
    while pos < len(value):
        if value[pos] != "\\":
            code = ord(value[pos])
            if code > 0x7f:
                raise ValueError("文字列はASCIIまたは\\xNNで指定してください。")
            result.append(code)
            pos += 1
            continue
        if pos + 1 < len(value) and value[pos + 1] == "\\":
            result.append(ord("\\"))
            pos += 2
            continue
        if pos + 3 < len(value) and value[pos + 1] == "x":
            try:
                result.append(int(value[pos + 2:pos + 4], 16))
            except ValueError as exc:
                raise ValueError("\\xの後には2桁の16進数が必要です。") from exc
            pos += 4
            continue
        raise ValueError("バックスラッシュは\\\\または\\xNNで指定してください。")
    if len(result) > 255:
        raise ValueError("文字列は255バイト以内です。")
    return bytes(result)


def check_coord(value: int, maximum: int, name: str) -> int:
    if not 0 <= value <= maximum:
        raise ValueError(f"{name}は0..{maximum}で指定してください。")
    return value


def encode_command(args: argparse.Namespace, sequence: int) -> bytes:
    command = COMMANDS[args.command]
    report = bytearray(REPORT_SIZE)
    report[0:3] = bytes((REPORT_ID, command, sequence))

    if args.command == "text":
        value = decode_text(args.value)
        if len(value) > TEXT_BYTES_PER_REPORT:
            raise ValueError("内部エラー: 文字列チャンクが19バイトを超えています。")
        report[3] = check_coord(args.column, 20, "column")
        report[4] = check_coord(args.row, 7, "row")
        report[5] = len(value)
        report[6:6 + len(value)] = value
    elif args.command in ("line", "rect"):
        report[3] = check_coord(args.x0, 127, "x0")
        report[4] = check_coord(args.y0, 63, "y0")
        report[5] = check_coord(args.x1, 127, "x1")
        report[6] = check_coord(args.y1, 63, "y1")
        if args.command == "rect" and (args.x0 > args.x1 or args.y0 > args.y1):
            raise ValueError("rectは左上、右下の順に指定してください。")
        if args.command == "rect":
            report[7] = 1 if args.fill else 0
    elif args.command == "circle":
        report[3] = check_coord(args.x, 127, "x")
        report[4] = check_coord(args.y, 63, "y")
        report[5] = check_coord(args.radius, 127, "radius")
        report[6] = 1 if args.fill else 0
    return bytes(report)


def encode_commands(args: argparse.Namespace, sequence: int) -> list[bytes]:
    """Create one report, or consecutive reports for one text command."""
    if args.command != "text":
        return [encode_command(args, sequence)]

    value = decode_text(args.value)
    column = check_coord(args.column, 20, "column")
    check_coord(args.row, 7, "row")
    # Only complete cells that can appear on the selected row need sending.
    visible = value[:21 - column]
    if not visible:
        visible = b""

    reports: list[bytes] = []
    for offset in range(0, max(1, len(visible)), TEXT_BYTES_PER_REPORT):
        chunk_args = argparse.Namespace(
            command="text",
            column=column + offset,
            row=args.row,
            value="",
        )
        report = bytearray(REPORT_SIZE)
        report[0:3] = bytes((REPORT_ID, COMMANDS["text"], sequence))
        report[3] = chunk_args.column
        report[4] = chunk_args.row
        chunk = visible[offset:offset + TEXT_BYTES_PER_REPORT]
        report[5] = len(chunk)
        report[6:6 + len(chunk)] = chunk
        reports.append(bytes(report))
        sequence = sequence % 255 + 1
    return reports


def decode_status(data: Sequence[int]) -> tuple[int, int, int, int, int]:
    values = list(data)
    # A few wrappers omit the report ID. Length distinguishes that case even
    # when a successful status byte happens to equal REPORT_ID (both are 1).
    offset = 1 if len(values) >= REPORT_SIZE and values[0] == REPORT_ID else 0
    if len(values) - offset < 5:
        raise RuntimeError(f"状態レポートが短すぎます（{len(values)}バイト）。")
    return tuple(int(v) for v in values[offset:offset + 5])  # type: ignore[return-value]


def read_status_from(dev: Any) -> tuple[int, int, int, int, int]:
    return decode_status(dev.get_feature_report(REPORT_ID, REPORT_SIZE))


def send_and_wait(report: bytes, timeout: float = 2.0) -> tuple[int, int, int, int, int]:
    expected_sequence = report[2]
    dev = open_device()
    try:
        result = dev.send_feature_report(report)
        if result is not None and result < 0:
            detail = dev.error() if hasattr(dev, "error") else "詳細なし"
            raise RuntimeError(f"Feature Reportの送信に失敗しました: {detail}")
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            time.sleep(0.02)
            status = read_status_from(dev)
            if status[2] == expected_sequence:
                return status
    finally:
        dev.close()
    raise RuntimeError("デバイスの処理完了を待つ間にタイムアウトしました。")


def read_status() -> tuple[int, int, int, int, int]:
    dev = open_device()
    try:
        return read_status_from(dev)
    finally:
        dev.close()


def print_status(status: tuple[int, int, int, int, int]) -> int:
    code, command, sequence, address, ready = status
    address_text = f"0x{address:02X}" if address else "未検出"
    print(
        f"status={STATUS.get(code, f'unknown-{code}')} "
        f"command={command} sequence={sequence} oled={address_text} ready={bool(ready)}"
    )
    if code == 4:
        print("確認: 電源、端子順、SDA/SCL、プルアップ電圧、I2Cアドレス")
    return 0 if code in (0, 1) else 1


def self_test() -> int:
    parser = build_parser()
    assert decode_text("ABC") == b"ABC"
    assert decode_text(r"A\x1f\x7f\\") == b"A\x1f\x7f\\"
    args = parser.parse_args(["text", "4", "7", r"Hi\x7f"])
    report = encode_commands(args, 23)[0]
    assert len(report) == REPORT_SIZE
    assert report[:9] == bytes((1, 4, 23, 4, 7, 3, ord("H"), ord("i"), 0x7f))
    args = parser.parse_args(["line", "0", "1", "127", "63"])
    assert encode_command(args, 1)[:7] == bytes((1, 5, 1, 0, 1, 127, 63))
    args = parser.parse_args(["rect", "2", "3", "20", "30", "--fill"])
    assert encode_command(args, 2)[:8] == bytes((1, 6, 2, 2, 3, 20, 30, 1))
    args = parser.parse_args(["circle", "64", "32", "12", "--fill"])
    assert encode_command(args, 3)[:7] == bytes((1, 7, 3, 64, 32, 12, 1))
    assert decode_status([1, 1, 9, 7, 0x3c, 1] + [0] * 19) == (1, 9, 7, 0x3c, 1)
    long_args = parser.parse_args(["text", "0", "0", "ABCDEFGHIJKLMNOPQRSTU"])
    chunks = encode_commands(long_args, 100)
    assert len(chunks) == 2
    assert chunks[0][2:6] == bytes((100, 0, 0, 19))
    assert chunks[1][2:6] == bytes((101, 19, 0, 2))
    assert chunks[0][6:25] + chunks[1][6:8] == b"ABCDEFGHIJKLMNOPQRSTU"
    for invalid in ("日本語", "A" * 256, r"\xzz"):
        try:
            decode_text(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid text accepted: {invalid!r}")
    print("oled_host self-test: PASS")
    return 0


def doctor() -> int:
    self_test()
    hid = import_hid()
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
    for name in ("output", "clear", "fill", "demo", "probe", "status"):
        sub.add_parser(name)
    text_parser = sub.add_parser("text")
    text_parser.add_argument("column", type=int)
    text_parser.add_argument("row", type=int)
    text_parser.add_argument("value")
    for name in ("line", "rect"):
        shape = sub.add_parser(name)
        shape.add_argument("x0", type=int)
        shape.add_argument("y0", type=int)
        shape.add_argument("x1", type=int)
        shape.add_argument("y1", type=int)
        if name == "rect":
            shape.add_argument("--fill", action="store_true", help="内部を塗りつぶす")
    circle = sub.add_parser("circle")
    circle.add_argument("x", type=int)
    circle.add_argument("y", type=int)
    circle.add_argument("radius", type=int)
    circle.add_argument("--fill", action="store_true", help="内部を塗りつぶす")
    return parser


def main() -> int:
    global _sequence
    args = build_parser().parse_args()
    try:
        if args.self_test:
            return self_test()
        if args.doctor:
            return doctor()
        if args.list:
            return print_devices()
        if args.command == "status":
            return print_status(read_status())
        if args.command not in COMMANDS:
            build_parser().print_help()
            return 2
        _sequence = int(time.monotonic_ns() & 0xff) or 1
        exit_code = 0
        for report in encode_commands(args, _sequence):
            exit_code = print_status(send_and_wait(report))
            if exit_code:
                return exit_code
        return exit_code
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
