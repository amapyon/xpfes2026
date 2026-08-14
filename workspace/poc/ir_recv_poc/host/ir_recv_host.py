#!/usr/bin/env python3
"""UIAPduinoで受信したNEC／東芝エアコン赤外線データを16進数表示する。"""
from __future__ import annotations

import argparse
import platform
import sys
import time
from typing import Iterable

VID = 0x1209
PID = 0xD009
PRODUCT = "UIAP IR Receiver PoC"
REPORT_LEN = 8

PROTOCOLS = {1: "NEC", 2: "NEC-extended", 3: "NEC-repeat"}
TOSHIBA_AC = 0x20


def import_hid():
    try:
        import hid  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "hidapiを読み込めません。Devkit環境で setup / doctor を実行してください。"
        ) from exc
    return hid


def matching_devices(hid_module) -> list[dict]:
    devices = list(hid_module.enumerate(VID, PID))
    exact = [d for d in devices if d.get("product_string") == PRODUCT]
    return exact if exact else devices


def open_one_device(hid_module):
    devices = matching_devices(hid_module)
    if not devices:
        raise RuntimeError(f"受信機 {VID:04X}:{PID:04X} が見つかりません")
    if len(devices) != 1:
        raise RuntimeError(f"受信機が{len(devices)}台あります。1台だけ接続してください")
    path = devices[0].get("path")
    if path is None:
        raise RuntimeError("HIDデバイスのパスを取得できません")
    if hasattr(hid_module, "device"):
        dev = hid_module.device()
        dev.open_path(path)
        return dev
    if hasattr(hid_module, "Device"):
        return hid_module.Device(path=path)
    raise RuntimeError("未対応のhidapi APIです")


def normalize_report(data: Iterable[int]) -> bytes:
    raw = bytes(data)
    if len(raw) == REPORT_LEN:
        return raw
    if len(raw) == REPORT_LEN + 1 and raw[0] == 0:
        return raw[1:]
    raise ValueError(f"HIDレポート長が不正です: {len(raw)}")


def decode_report(data: Iterable[int]) -> dict:
    raw = normalize_report(data)
    sequence, protocol = raw[0], raw[1]
    if protocol == 0x10:
        return {
            "kind": "status", "input_high": bool(raw[2]), "state": raw[3],
            "edges": int.from_bytes(raw[4:6], "little"),
            "errors": raw[6], "bits_max": raw[7],
        }
    if protocol in (0x11, 0x12):
        return {
            "kind": "timing", "page": "last" if protocol == 0x11 else "max",
            "mark_us": int.from_bytes(raw[2:4], "little"),
            "space_us": int.from_bytes(raw[4:6], "little"),
        }
    if protocol == 0x13:
        return {
            "kind": "reject", "reason": raw[2], "state": raw[3],
            "duration_us": int.from_bytes(raw[4:6], "little"),
            "bits_max": raw[6], "errors": raw[7],
        }
    if protocol == TOSHIBA_AC:
        return {
            "kind": "fragment", "sequence": sequence,
            "index": raw[2], "length": raw[3], "payload": raw[4:8],
        }
    if protocol not in PROTOCOLS:
        raise ValueError(f"未対応のプロトコル番号です: {protocol}")
    code_bytes = raw[2:6]
    flags = raw[6]
    standard_address = protocol == 1 or (protocol == 3 and bool(flags & 1))
    address = code_bytes[0] if standard_address else int.from_bytes(code_bytes[:2], "little")
    return {
        "kind": "code", "sequence": sequence, "protocol": PROTOCOLS[protocol],
        "repeat": protocol == 3, "code": "0x" + code_bytes.hex().upper(),
        "address": address, "command": code_bytes[2],
        "address_inverse_ok": bool(flags & 1), "command_inverse_ok": bool(flags & 2),
    }


class ToshibaAssembler:
    """8-byte HIDレポートに分割された最大10バイトの状態を復元する。"""

    def __init__(self) -> None:
        self.sequence: int | None = None
        self.length = 0
        self.parts: dict[int, bytes] = {}

    def add(self, fragment: dict) -> dict | None:
        length = fragment["length"]
        index = fragment["index"]
        if length not in (7, 9, 10) or index >= 3:
            return None
        if self.sequence != fragment["sequence"] or self.length != length:
            self.sequence = fragment["sequence"]
            self.length = length
            self.parts = {}
        self.parts[index] = bytes(fragment["payload"])
        needed = (length + 3) // 4
        if any(i not in self.parts for i in range(needed)):
            return None
        data = b"".join(self.parts[i] for i in range(needed))[:length]
        self.parts = {}
        return {
            "kind": "toshiba", "sequence": self.sequence,
            "protocol": "TOSHIBA_AC", "bits": length * 8,
            "code": "0x" + data.hex().upper(), "data": data,
        }


def print_event(event: dict) -> None:
    if event["kind"] == "toshiba":
        print(
            f'{event["code"]}  {event["protocol"]}  '
            f'{event["bits"]}bit checksum=OK', flush=True,
        )
        return
    suffix = " (repeat)" if event["repeat"] else ""
    width = 2 if event["address"] <= 0xFF else 4
    print(
        f'{event["code"]}  {event["protocol"]}{suffix}  '
        f'address=0x{event["address"]:0{width}X}  '
        f'command=0x{event["command"]:02X}', flush=True,
    )


def self_test() -> int:
    event = decode_report(bytes([7, 1, 0x20, 0xDF, 0x10, 0xEF, 3, 32]))
    assert event["code"] == "0x20DF10EF" and event["address"] == 0x20
    assert event["command"] == 0x10 and event["command_inverse_ok"]
    ext = decode_report(bytes([8, 2, 0x34, 0x12, 0x56, 0xA9, 2, 32]))
    assert ext["address"] == 0x1234 and ext["command"] == 0x56
    repeat = decode_report(bytes([9, 3, 0x20, 0xDF, 0x10, 0xEF, 3, 32]))
    assert repeat["repeat"] and repeat["address"] == 0x20
    status = decode_report(bytes([12, 0x10, 1, 0, 12, 0, 0, 0]))
    assert status["kind"] == "status" and status["edges"] == 12
    timing = decode_report(bytes([12, 0x12, 0x28, 0x23, 0x94, 0x11, 0, 0]))
    assert timing["mark_us"] == 9000 and timing["space_us"] == 4500

    # Toshiba 72bit sample. The assembler must also accept out-of-order fragments.
    sample = bytes.fromhex("F20D03FC0150000051")
    assembler = ToshibaAssembler()
    reports = [
        bytes([21, TOSHIBA_AC, 1, 9]) + sample[4:8],
        bytes([21, TOSHIBA_AC, 0, 9]) + sample[0:4],
        bytes([21, TOSHIBA_AC, 2, 9]) + sample[8:] + bytes(3),
    ]
    result = None
    for report in reports:
        result = assembler.add(decode_report(report)) or result
    assert result and result["code"] == "0x" + sample.hex().upper()
    assert result["bits"] == 72
    print("ホスト側セルフテスト: PASS")
    return 0


def list_devices(hid_module) -> int:
    devices = matching_devices(hid_module)
    print(f"該当デバイス: {len(devices)}台")
    for index, device in enumerate(devices):
        print(f'[{index}] {VID:04X}:{PID:04X} {device.get("product_string") or ""}')
    return 0 if devices else 1


def monitor() -> int:
    hid_module = import_hid()
    dev = open_one_device(hid_module)
    previous_sequence = 0
    last_status_time = 0.0
    assembler = ToshibaAssembler()
    timing = {
        "last_mark": 0, "last_space": 0, "max_mark": 0, "max_space": 0,
        "reject_reason": 0, "reject_state": 0, "reject_duration": 0,
    }
    print(f"接続しました: {VID:04X}:{PID:04X} {PRODUCT}")
    print("赤外線信号を待っています。終了は Ctrl+C です。")
    try:
        while True:
            data = dev.read(REPORT_LEN, 500)
            if not data:
                continue
            try:
                event = decode_report(data)
            except ValueError:
                continue
            if event["kind"] == "status":
                now = time.monotonic()
                if now - last_status_time >= 1.0:
                    level = "HIGH（待機）" if event["input_high"] else "LOW（受信中/配線確認）"
                    print(
                        f'状態: OUT={level} edges={event["edges"]} '
                        f'state={event["state"]} bits_max={event["bits_max"]} '
                        f'errors={event["errors"]}  '
                        f'last={timing["last_mark"]}/{timing["last_space"]}us '
                        f'max={timing["max_mark"]}/{timing["max_space"]}us  '
                        f'reject={timing["reject_reason"]}/state{timing["reject_state"]}/'
                        f'{timing["reject_duration"]}us', flush=True,
                    )
                    last_status_time = now
                continue
            if event["kind"] == "timing":
                timing[event["page"] + "_mark"] = event["mark_us"]
                timing[event["page"] + "_space"] = event["space_us"]
                continue
            if event["kind"] == "reject":
                timing["reject_reason"] = event["reason"]
                timing["reject_state"] = event["state"]
                timing["reject_duration"] = event["duration_us"]
                continue
            if event["kind"] == "fragment":
                completed = assembler.add(event)
                if completed:
                    print_event(completed)
                continue
            if event["sequence"] != previous_sequence:
                previous_sequence = event["sequence"]
                print_event(event)
    except KeyboardInterrupt:
        print("\n終了しました。")
        return 0
    finally:
        dev.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="該当HIDデバイスを表示")
    parser.add_argument("--self-test", action="store_true", help="USBなしで表示処理を検証")
    parser.add_argument("--doctor", action="store_true", help="ホスト環境を診断")
    args = parser.parse_args()
    try:
        if args.self_test:
            return self_test()
        if args.doctor:
            self_test()
            hid_module = import_hid()
            print(f"Python: {platform.python_version()}")
            print(f"hidapi: PASS ({getattr(hid_module, '__version__', 'unknown')})")
            return 0
        if args.list:
            return list_devices(import_hid())
        return monitor()
    except (RuntimeError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
