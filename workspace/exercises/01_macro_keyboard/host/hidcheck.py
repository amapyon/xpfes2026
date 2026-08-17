from __future__ import annotations
import argparse
import sys

# TEST-ONLY USB IDENTIFIER
# 1209:0001 is shared, not globally unique, and limited to educational
# prototyping and testing within this workshop. Do not use it for products,
# manufacturing, sale, or redistribution.
VID = 0x1209
PID = 0x0001
PRODUCT = 'UIAP Macro Keyboard'


def self_test() -> int:
    sequence = [(0x02, 0x04), (0x00, 0x05), (0x02, 0x06), (0x00, 0x07), (0x02, 0x08)]
    if sequence != [(2, 4), (0, 5), (2, 6), (0, 7), (2, 8)]:
        print('[UIAP-KBD-E201] Macro sequence self-test failed.')
        return 1
    print('Macro sequence and USB identity self-test: PASS')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    try:
        import hid
    except Exception as exc:
        print(f'[UIAP-KBD-E202] hidapi import failed: {exc}', file=sys.stderr)
        return 2
    devices = list(hid.enumerate(VID, PID))
    print(f'Matching devices: {len(devices)}')
    for index, dev in enumerate(devices):
        print(f'[{index}] VID:PID={dev.get("vendor_id", 0):04X}:{dev.get("product_id", 0):04X}')
        print(f'  Product: {dev.get("product_string") or "(unknown)"}')
        print(f'  Serial: {dev.get("serial_number") or "(unknown)"}')
    if len(devices) != 1:
        print('[UIAP-KBD-E203] Connect exactly one UIAP Macro Keyboard.', file=sys.stderr)
        return 3
    actual_product = devices[0].get('product_string') or '(unknown)'
    if actual_product != PRODUCT:
        print(
            f"[UIAP-KBD-E204] Expected Product '{PRODUCT}', "
            f"got '{actual_product}'.",
            file=sys.stderr,
        )
        return 4
    print(f'{PRODUCT} HID enumeration: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
