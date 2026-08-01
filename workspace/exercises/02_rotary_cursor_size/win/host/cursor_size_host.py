from __future__ import annotations

import argparse
import ctypes
import json
import os
from pathlib import Path
import sys
import time
from typing import Any

VID = 0x1209
PID = 0xC004
STEP = 16
MIN_SIZE = 32
MAX_SIZE = 256
CURSOR_REG_PATH = r"Control Panel\Cursors"
CURSOR_REG_NAME = "CursorBaseSize"
ACCESS_REG_PATH = r"Software\Microsoft\Accessibility"
ACCESS_REG_NAME = "CursorSize"
# Undocumented Windows 10/11 action used by the project's validated v1.0.7 PoC.
# Do not add the legacy cursor-reload call; it regressed to WinError 6.
SPI_SET_POINTER_SIZE = 0x2029
SPIF_UPDATEINIFILE = 0x0001
STATE_SCHEMA = 2


def state_path() -> Path:
    root = os.environ.get('UIAP_DEVKIT_ROOT')
    if not root:
        raise RuntimeError('UIAP_DEVKIT_ROOT is not set. Start with start-uiap.cmd.')
    return Path(root) / '.state' / 'cursor-size-before.json'


def enumerate_devices() -> list[dict[str, Any]]:
    import hid
    return list(hid.enumerate(VID, PID))


def print_devices(devices: list[dict[str, Any]]) -> None:
    print(f'Matching devices: {len(devices)}')
    for index, dev in enumerate(devices):
        print(f'[{index}] VID:PID={dev.get("vendor_id", 0):04X}:{dev.get("product_id", 0):04X}')
        print(f'  Product: {dev.get("product_string") or "(unknown)"}')
        print(f'  Serial: {dev.get("serial_number") or "(unknown)"}')


def require_one_device() -> dict[str, Any]:
    devices = enumerate_devices()
    print_devices(devices)
    if len(devices) != 1:
        raise RuntimeError('[UIAP-CURSOR-E201] Connect exactly one rotary cursor device.')
    return devices[0]


def clamp_size(size: int) -> int:
    return max(MIN_SIZE, min(MAX_SIZE, int(size)))


def slider_from_size(size: int) -> int:
    size = clamp_size(size)
    return ((size - MIN_SIZE) // STEP) + 1


def _read_registry_value(path: str, name: str, *, required: bool) -> dict[str, Any]:
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_READ) as key:
            value, value_type = winreg.QueryValueEx(key, name)
        return {'exists': True, 'value': value, 'type': int(value_type)}
    except FileNotFoundError:
        if required:
            raise RuntimeError(f'[UIAP-CURSOR-E202] Registry value not found: HKCU\\{path}\\{name}')
        return {'exists': False, 'value': None, 'type': None}


def _write_registry_value(path: str, name: str, value: Any, value_type: int) -> None:
    import winreg
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, name, 0, value_type, value)


def _restore_registry_value(path: str, name: str, entry: dict[str, Any]) -> None:
    import winreg
    if entry.get('exists'):
        _write_registry_value(path, name, entry.get('value'), int(entry.get('type')))
        return
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, name)
    except FileNotFoundError:
        pass


def read_cursor_size() -> int:
    if os.name != 'nt':
        raise RuntimeError('[UIAP-CURSOR-E203] Cursor size control is supported only on Windows.')
    entry = _read_registry_value(CURSOR_REG_PATH, CURSOR_REG_NAME, required=True)
    return int(entry['value'])


def snapshot_cursor_state() -> dict[str, Any]:
    if os.name != 'nt':
        raise RuntimeError('[UIAP-CURSOR-E203] Cursor size control is supported only on Windows.')
    return {
        'schema': STATE_SCHEMA,
        'cursor_base': _read_registry_value(CURSOR_REG_PATH, CURSOR_REG_NAME, required=True),
        'accessibility': _read_registry_value(ACCESS_REG_PATH, ACCESS_REG_NAME, required=False),
    }


def _call_pointer_size_api(size: int) -> None:
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    spi = user32.SystemParametersInfoW
    spi.argtypes = [ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint]
    spi.restype = ctypes.c_bool
    ctypes.set_last_error(0)
    ok = spi(SPI_SET_POINTER_SIZE, 0, ctypes.c_void_p(size), SPIF_UPDATEINIFILE)
    if not ok:
        err = ctypes.get_last_error()
        if err:
            raise ctypes.WinError(err)
        raise RuntimeError('[UIAP-CURSOR-E204] Pointer-size API returned FALSE without a Windows error code.')


def apply_cursor_size(size: int) -> None:
    if os.name != 'nt':
        raise RuntimeError('[UIAP-CURSOR-E203] Cursor size control is supported only on Windows.')
    import winreg
    size = clamp_size(size)
    _write_registry_value(CURSOR_REG_PATH, CURSOR_REG_NAME, size, winreg.REG_DWORD)
    _write_registry_value(ACCESS_REG_PATH, ACCESS_REG_NAME, slider_from_size(size), winreg.REG_DWORD)
    _call_pointer_size_api(size)
    actual = read_cursor_size()
    if actual != size:
        raise RuntimeError(f'[UIAP-CURSOR-E205] CursorBaseSize verification failed: expected={size} actual={actual}')


def _normalize_saved_state(raw: dict[str, Any]) -> dict[str, Any]:
    if raw.get('schema') == STATE_SCHEMA and 'cursor_base' in raw:
        return raw
    # Backward compatibility with test17/test18 state files.
    if 'size' in raw:
        size = int(raw['size'])
        value_type = int(raw.get('type', 4))
        return {
            'schema': STATE_SCHEMA,
            'cursor_base': {'exists': True, 'value': size, 'type': value_type},
            'accessibility': {
                'exists': True,
                'value': slider_from_size(size),
                'type': 4,
            },
        }
    raise RuntimeError('[UIAP-CURSOR-E206] Saved cursor state format is not supported.')


def save_state(snapshot: dict[str, Any]) -> None:
    path = state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding='utf-8')


def restore_snapshot(snapshot: dict[str, Any]) -> int:
    normalized = _normalize_saved_state(snapshot)
    base = normalized['cursor_base']
    _restore_registry_value(CURSOR_REG_PATH, CURSOR_REG_NAME, base)
    _restore_registry_value(ACCESS_REG_PATH, ACCESS_REG_NAME, normalized['accessibility'])
    _call_pointer_size_api(int(base['value']))
    actual = read_cursor_size()
    if actual != int(base['value']):
        raise RuntimeError(f'[UIAP-CURSOR-E207] Restore verification failed: expected={base["value"]} actual={actual}')
    return actual


def restore_state(remove: bool = True) -> int:
    path = state_path()
    if not path.exists():
        print('[UIAP-CURSOR-E208] Saved cursor state was not found.', file=sys.stderr)
        return 3
    raw = json.loads(path.read_text(encoding='utf-8'))
    restored = restore_snapshot(raw)
    print(f'Restored pointer size: {restored}')
    if remove:
        path.unlink(missing_ok=True)
    return 0


def recover_stale_state() -> None:
    path = state_path()
    if not path.exists():
        return
    print('Saved cursor state from a previous interrupted run was found. Restoring it first.')
    restore_state(remove=True)


def decode_delta(data: list[int]) -> int:
    if not data:
        return 0
    # This device has no HID Report ID. hidapi therefore returns the payload
    # as-is on Windows. The macOS test13 firmware uses byte 0 for delta and
    # byte 1 for a diagnostic sequence counter. A neutral delta must not be
    # mistaken for a leading Report ID, or the counter looks like movement.
    raw = data[0]
    return raw - 256 if raw >= 128 else raw


def open_device():
    import hid
    require_one_device()
    dev = hid.device()
    dev.open(VID, PID)
    return dev


def run_events(dry_run: bool) -> int:
    dev = open_device()
    original: dict[str, Any] | None = None
    current_size: int | None = None
    try:
        if not dry_run:
            recover_stale_state()
            original = snapshot_cursor_state()
            current_size = int(original['cursor_base']['value'])
            save_state(original)
            print(f'Original pointer size: {current_size}')
        print('Mode: dry-run' if dry_run else 'Mode: apply')
        print('Rotate the encoder. Press Ctrl+C to stop.')
        while True:
            data = dev.read(8, 500)
            delta = decode_delta(data)
            if delta == 0:
                continue
            direction = 'CW' if delta > 0 else 'CCW'
            if dry_run:
                print(f'{direction} delta={delta}')
                continue
            assert current_size is not None
            next_size = clamp_size(current_size + STEP * delta)
            if next_size != current_size:
                apply_cursor_size(next_size)
                current_size = next_size
            print(f'{direction}: {current_size}')
    except KeyboardInterrupt:
        print('Stopping.')
    finally:
        try:
            dev.close()
        except Exception:
            pass
        if not dry_run and original is not None:
            try:
                restored = restore_snapshot(original)
            except Exception as exc:
                print(f'[UIAP-CURSOR-E209] Automatic restore failed: {exc}', file=sys.stderr)
                print('Run make restore after updating the host application.', file=sys.stderr)
            else:
                state_path().unlink(missing_ok=True)
                print(f'Restored pointer size: {restored}')
    return 0


def cursor_test() -> int:
    if os.name != 'nt':
        raise RuntimeError('[UIAP-CURSOR-E203] Cursor size control is supported only on Windows.')
    recover_stale_state()
    original = snapshot_cursor_state()
    original_size = int(original['cursor_base']['value'])
    target = original_size + STEP if original_size <= MAX_SIZE - STEP else original_size - STEP
    save_state(original)
    try:
        print(f'Cursor test: {original_size} -> {target}')
        apply_cursor_size(target)
        time.sleep(0.8)
        print(f'Applied pointer size: {read_cursor_size()}')
    finally:
        restored = restore_snapshot(original)
        state_path().unlink(missing_ok=True)
        print(f'Restored pointer size: {restored}')
    print('Windows pointer-size apply/restore test: PASS')
    return 0


def self_test() -> int:
    cases = [
        ([1], 1),
        ([255], -1),
        ([0, 221], 0),
        ([1, 222], 1),
        ([255, 223], -1),
        ([], 0),
    ]
    for data, expected in cases:
        actual = decode_delta(data)
        if actual != expected:
            print(f'[UIAP-CURSOR-E210] decode test failed: {data} -> {actual}', file=sys.stderr)
            return 4
    values = [clamp_size(80 + STEP * d) for d in (-10, -1, 1, 20)]
    if values != [32, 64, 96, 256]:
        print('[UIAP-CURSOR-E211] cursor mapping self-test failed.', file=sys.stderr)
        return 5
    sliders = [slider_from_size(v) for v in (32, 48, 80, 256)]
    if sliders != [1, 2, 4, 15]:
        print(f'[UIAP-CURSOR-E212] accessibility slider mapping failed: {sliders}', file=sys.stderr)
        return 6
    migrated = _normalize_saved_state({'size': 80, 'type': 4})
    if migrated['cursor_base']['value'] != 80 or migrated['accessibility']['value'] != 4:
        print('[UIAP-CURSOR-E213] legacy state migration failed.', file=sys.stderr)
        return 7
    print('Host protocol, cursor mapping, and state migration self-test: PASS')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['list', 'hidcheck', 'dry-run', 'app', 'restore', 'cursor-test', 'self-test'])
    args = parser.parse_args()
    try:
        if args.command == 'self-test':
            return self_test()
        if args.command == 'list':
            print_devices(enumerate_devices())
            return 0
        if args.command == 'hidcheck':
            require_one_device()
            print('Rotary cursor HID enumeration: PASS')
            return 0
        if args.command == 'restore':
            return restore_state()
        if args.command == 'cursor-test':
            return cursor_test()
        return run_events(args.command == 'dry-run')
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
