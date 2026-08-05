#!/usr/bin/env python3
"""UIAPduino Vendor-defined HID preflight test using 8-byte Feature Reports."""
from __future__ import annotations

import secrets
import time

try:
    import hid
except Exception as exc:
    print("[FAIL] hidapi could not be imported.")
    print(f"detail: {exc}")
    raise SystemExit(2)

VID = 0x1209
PID = 0xD003
REPORT_ID = 0x01
REPORT_LEN = 8
EXPECTED_PRODUCT = "UIAP HID Preflight"
EXPECTED_PROTOCOL = (1, 2)
EXPECTED_FIRMWARE = (1, 0, 2)
EXPECTED_BOARD = "UIAPduino Pro Micro CH32V003 V1.4"

CMD_PING = 0x01
CMD_GET_INFO = 0x02
CMD_GET_BOARD = 0x03
CMD_GET_MCU_ID = 0x04
RSP_PONG = 0x81
RSP_INFO = 0x82
RSP_BOARD = 0x83
RSP_MCU_ID = 0x84
STATUS_OK = 0x01
BOARD_CHUNK_BYTES = 5
MCU_ID_BYTES = 8
MCU_ID_CHUNK_BYTES = 5


def format_minichlink_part_uuid(raw: bytes) -> str:
    """Format the 8-byte MCU ID like minichlink Part UUID output.

    CH32V003 exposes the ID as two little-endian 32-bit words. minichlink
    prints each word most-significant byte first, so reverse each 4-byte
    group while preserving the word order.
    """
    if len(raw) != MCU_ID_BYTES:
        raise ValueError(f"MCU ID must be {MCU_ID_BYTES} bytes")
    ordered = raw[0:4][::-1] + raw[4:8][::-1]
    return "-".join(f"{b:02x}" for b in ordered)


def matching_devices():
    return [d for d in hid.enumerate(VID, PID)
            if (d.get("product_string") or "") == EXPECTED_PRODUCT]


def open_device():
    devices = matching_devices()
    if not devices:
        raise RuntimeError(f"preflight HID device {VID:04X}:{PID:04X} was not found")
    if len(devices) != 1:
        raise RuntimeError(f"expected one preflight HID device, found {len(devices)}")
    dev = hid.device()
    path = devices[0].get("path")
    if path:
        dev.open_path(path)
    else:
        dev.open(VID, PID)
    return dev, devices[0]


def normalize(data):
    raw = bytes(data)
    if len(raw) == REPORT_LEN:
        return raw
    if len(raw) == REPORT_LEN - 1:
        return bytes([REPORT_ID]) + raw
    raise RuntimeError(f"unexpected Feature Report length: {len(raw)}")


def transact(dev, request: bytes, expected_response: int, predicate=None, timeout=2.0):
    if len(request) != REPORT_LEN:
        raise ValueError("request must be exactly 8 bytes")
    written = dev.send_feature_report(request)
    if written <= 0:
        raise RuntimeError(f"send_feature_report returned {written}")

    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        raw = normalize(dev.get_feature_report(REPORT_ID, REPORT_LEN))
        last = raw
        if raw[0] == REPORT_ID and raw[1] == expected_response:
            if predicate is None or predicate(raw):
                return raw
        time.sleep(0.02)

    detail = last.hex(" ") if last is not None else "no report"
    raise RuntimeError(f"response 0x{expected_response:02X} timed out; last={detail}")


def req(command: int, arg: int = 0) -> bytearray:
    out = bytearray(REPORT_LEN)
    out[0] = REPORT_ID
    out[1] = command
    out[2] = arg & 0xff
    return out


def main() -> int:
    print("========================================")
    print(" UIAPduino HID Preflight")
    print("========================================")

    try:
        dev, info = open_device()
    except Exception as exc:
        print("[FAIL] USB HID enumeration")
        print(f"detail: {exc}")
        return 3

    try:
        print(f"[PASS] USB HID enumeration  {VID:04X}:{PID:04X} {info.get('product_string') or ''}")

        nonce = secrets.randbits(32)
        ping = req(CMD_PING)
        ping[2:6] = nonce.to_bytes(4, "little")
        pong = transact(
            dev, ping, RSP_PONG,
            lambda r: int.from_bytes(r[2:6], "little") == nonce,
        )
        returned_nonce = int.from_bytes(pong[2:6], "little")
        if pong[6] != STATUS_OK:
            raise RuntimeError(f"device returned status 0x{pong[6]:02X}")
        print(f"[PASS] Host -> device       nonce=0x{nonce:08X}")
        print(f"[PASS] Device -> host       nonce=0x{returned_nonce:08X}")

        info_report = transact(dev, req(CMD_GET_INFO), RSP_INFO)
        protocol = (info_report[2], info_report[3])
        firmware = (info_report[4], info_report[5], info_report[6])
        board_len = info_report[7]

        if board_len <= 0 or board_len > 100:
            raise RuntimeError(f"invalid board target length: {board_len}")

        chunks = []
        chunk_count = (board_len + BOARD_CHUNK_BYTES - 1) // BOARD_CHUNK_BYTES
        for index in range(chunk_count):
            board_report = transact(
                dev, req(CMD_GET_BOARD, index), RSP_BOARD,
                lambda r, i=index: r[2] == i,
            )
            chunks.append(board_report[3:8])
        board = b"".join(chunks)[:board_len].decode("ascii")

        mcu_chunks = []
        mcu_chunk_count = (MCU_ID_BYTES + MCU_ID_CHUNK_BYTES - 1) // MCU_ID_CHUNK_BYTES
        for index in range(mcu_chunk_count):
            mcu_report = transact(
                dev, req(CMD_GET_MCU_ID, index), RSP_MCU_ID,
                lambda r, i=index: r[2] == i,
            )
            mcu_chunks.append(mcu_report[3:8])
        mcu_id = b"".join(mcu_chunks)[:MCU_ID_BYTES]
        if len(mcu_id) != MCU_ID_BYTES or not any(mcu_id):
            raise RuntimeError("invalid MCU ID returned by device")
        mcu_id_text = format_minichlink_part_uuid(mcu_id)

        checks = [
            ("Protocol version", protocol == EXPECTED_PROTOCOL, ".".join(map(str, protocol))),
            ("Firmware version", firmware == EXPECTED_FIRMWARE, ".".join(map(str, firmware))),
            ("Board target", board == EXPECTED_BOARD, board),
            ("MCU ID", True, mcu_id_text),
            ("Random nonce", returned_nonce == nonce, f"0x{returned_nonce:08X}"),
        ]
        failed = False
        for label, ok, value in checks:
            print(f"[{'PASS' if ok else 'FAIL'}] {label:<20} {value}")
            failed |= not ok

        print()
        if failed:
            print("RESULT: FAIL")
            return 4
        print("RESULT: PASS")
        print("UIAPduino is operating as a Vendor-defined USB HID device.")
        return 0
    except Exception as exc:
        print("[FAIL] HID ping/pong")
        print(f"detail: {exc}")
        print()
        print("RESULT: FAIL")
        return 5
    finally:
        try:
            dev.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
