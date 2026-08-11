#!/usr/bin/env python3
"""04_rotary_cursor_haptic用のWindows/macOS共通ホストアプリ。"""

from __future__ import annotations

import argparse
import ctypes
import json
import math
import os
from pathlib import Path
import struct
import sys
import time
from typing import Any

VERSION = "0.5.0"

# rotary_cursor_size.cが通知するUSB識別子。
# 派生演習や製品を作る場合は、ファームウェア側と同時に変更する。
VID = 0x1209
PID = 0xC005
PRODUCT = "UIAP Rotary Haptic"
ENCODER_REPORT_ID = 0x01
HAPTIC_REPORT_ID = 0x02
HAPTIC_DELAY_SECONDS = 0.2
HAPTIC_NORMAL_PATTERN = (95, 80, 40, 2)
HAPTIC_LIMIT_PATTERN = (95, 250, 0, 1)

# 参加者が調整しやすいWindows用の値。
# STEPはエンコーダー1刻みの変化量、MIN/MAXは変更可能な範囲を表す。
WIN_STEP = 16
WIN_MIN = 32
WIN_MAX = 256

# 以下はWindowsのレジストリ/API用定数。
# カーソルサイズの変化量だけを調整する場合は、通常変更しない。
WIN_CURSOR_REG_PATH = r"Control Panel\Cursors"
WIN_CURSOR_REG_NAME = "CursorBaseSize"
WIN_ACCESS_REG_PATH = r"Software\Microsoft\Accessibility"
WIN_ACCESS_REG_NAME = "CursorSize"
WIN_SPI_SET_POINTER_SIZE = 0x2029
WIN_SPIF_UPDATEINIFILE = 0x0001
WIN_STATE_SCHEMA = 2

# macOSは整数のピクセル値ではなく倍率を使用する。
# 次の3値がmacOSでの主なカスタマイズ箇所となる。
MAC_STEP = 0.25
MAC_MIN = 0.50
MAC_MAX = 4.00

# OBSERVED範囲は、非公開APIから返された異常値を除外するためだけに使う。
# 参加者向けの変更範囲であるMIN/MAXとは意図的に分けている。
MAC_OBSERVED_MIN = 0.25
MAC_OBSERVED_MAX = 16.00
MAC_COMPARE_TOLERANCE = 0.02
MAC_PROBE_BITS = 0x7FF8000000000000
MAC_PROBE_HIGH_WORD = 0x7FF80000


def import_hid():
    try:
        import hid
    except Exception as exc:
        raise RuntimeError(
            "[UIAP-CURSOR-E203] Could not import bundled hidapi: "
            f"{exc}"
        ) from exc
    return hid


def enumerate_devices() -> list[dict[str, Any]]:
    return list(import_hid().enumerate(VID, PID))


def print_devices(devices: list[dict[str, Any]]) -> None:
    print(f"Matching devices: {len(devices)}")
    for index, info in enumerate(devices):
        print(
            f"[{index}] VID:PID="
            f"{info.get('vendor_id', VID):04X}:"
            f"{info.get('product_id', PID):04X}"
        )
        print(f"  Product: {info.get('product_string') or '(unknown)'}")
        print(f"  Serial: {info.get('serial_number') or '(unknown)'}")


def require_one_device() -> dict[str, Any]:
    devices = enumerate_devices()
    print_devices(devices)
    if len(devices) != 1:
        raise RuntimeError(
            "[UIAP-CURSOR-E201] Connect exactly one rotary cursor device."
        )
    actual_product = devices[0].get("product_string") or "(unknown)"
    if actual_product != PRODUCT:
        raise RuntimeError(
            f"[UIAP-CURSOR-E219] Expected Product '{PRODUCT}', "
            f"got '{actual_product}'."
        )
    return devices[0]


def open_device():
    hid = import_hid()
    info = require_one_device()
    dev = hid.device()
    path = info.get("path")
    if path is not None:
        dev.open_path(path)
    else:
        dev.open(VID, PID)
    return dev


def decode_delta(data: list[int]) -> int:
    """Report ID 1付きの[ID, delta, sequence]を復号する。"""
    if not data:
        return 0
    # 現行03ファームウェアはReport ID 1を先頭に付ける。
    # 更新前の2バイト形式も診断できるよう、IDなしの入力も受け付ける。
    offset = 1 if data[0] == ENCODER_REPORT_ID and len(data) >= 3 else 0
    raw = int(data[offset]) & 0xFF
    return raw - 256 if raw >= 128 else raw


def encode_haptic_pattern(pattern: tuple[int, int, int, int]) -> bytes:
    """[ID, level, on_ms LE16, off_ms LE16, count]を生成する。"""
    level, on_ms, off_ms, count = pattern
    if not 0 <= level <= 100:
        raise ValueError("haptic level must be between 0 and 100")
    if not 0 <= on_ms <= 5000 or not 0 <= off_ms <= 5000:
        raise ValueError("haptic ON/OFF time must be between 0 and 5000ms")
    if not 0 <= count <= 255:
        raise ValueError("haptic count must be between 0 and 255")
    if level > 0 and count > 0 and on_ms == 0:
        raise ValueError("finite haptic pattern requires a positive ON time")
    return bytes(
        (
            HAPTIC_REPORT_ID,
            level,
            on_ms & 0xFF,
            (on_ms >> 8) & 0xFF,
            off_ms & 0xFF,
            (off_ms >> 8) & 0xFF,
            count,
        )
    )


def trigger_haptic(dev: Any, pattern: tuple[int, int, int, int]) -> None:
    """Feature Report ID 2で振動パターン一式を指示する。"""
    result = dev.send_feature_report(encode_haptic_pattern(pattern))
    if result is not None and result < 0:
        raise RuntimeError(
            "[UIAP-CURSOR-E217] Haptic Feature Report failed."
        )


class HapticScheduler:
    """最後の回転から一定時間が経過するまで触覚指示を保留する。"""

    def __init__(self) -> None:
        self.pattern: tuple[int, int, int, int] | None = None
        self.deadline = 0.0

    def schedule(self, pattern: tuple[int, int, int, int], now: float) -> None:
        # 連続回転中は、最後に発生した結果と停止時刻で上書きする。
        self.pattern = pattern
        self.deadline = now + HAPTIC_DELAY_SECONDS

    def take_due(self, now: float) -> tuple[int, int, int, int] | None:
        if self.pattern is None or now < self.deadline:
            return None
        pattern = self.pattern
        self.pattern = None
        return pattern


def devkit_root() -> Path:
    root = os.environ.get("UIAP_DEVKIT_ROOT")
    if not root:
        raise RuntimeError(
            "UIAP_DEVKIT_ROOT is not set. Start the UIAP Devkit first."
        )
    return Path(root)


class WindowsCursorBackend:
    """Windows固有の状態保存とポインターサイズ操作を提供する。

    共通イベントループは、このバックエンドの公開メソッドだけを使用する。
    別OSへ対応するときも、同じ読取り・保存・適用・復元用メソッドを実装する。
    """

    name = "Windows"

    def state_path(self) -> Path:
        # 統合前のWindows版と互換性のある状態ファイル名を維持する。
        return (
            devkit_root()
            / ".state"
            / "04_rotary_cursor_haptic.cursor-size-before.json"
        )

    @staticmethod
    def clamp(value: int | float) -> int:
        return max(WIN_MIN, min(WIN_MAX, int(value)))

    @staticmethod
    def slider_from_size(value: int | float) -> int:
        # Windowsは、1始まりのアクセシビリティ用スライダー値も保存する。
        size = WindowsCursorBackend.clamp(value)
        return ((size - WIN_MIN) // WIN_STEP) + 1

    @staticmethod
    def equal(left: int | float, right: int | float) -> bool:
        return int(left) == int(right)

    @staticmethod
    def format_value(value: int | float) -> str:
        return str(int(value))

    @staticmethod
    def next_value(current: int | float, delta: int) -> int:
        return WindowsCursorBackend.clamp(
            int(current) + WIN_STEP * delta
        )

    @staticmethod
    def _read_registry(
        path: str,
        name: str,
        *,
        required: bool,
    ) -> dict[str, Any]:
        import winreg

        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                path,
                0,
                winreg.KEY_READ,
            ) as key:
                value, value_type = winreg.QueryValueEx(key, name)
            return {
                "exists": True,
                "value": value,
                "type": int(value_type),
            }
        except FileNotFoundError:
            if required:
                raise RuntimeError(
                    "[UIAP-CURSOR-E202] Registry value not found: "
                    f"HKCU\\{path}\\{name}"
                )
            return {"exists": False, "value": None, "type": None}

    @staticmethod
    def _write_registry(
        path: str,
        name: str,
        value: Any,
        value_type: int,
    ) -> None:
        import winreg

        with winreg.CreateKeyEx(
            winreg.HKEY_CURRENT_USER,
            path,
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            winreg.SetValueEx(key, name, 0, value_type, value)

    @classmethod
    def _restore_registry(
        cls,
        path: str,
        name: str,
        entry: dict[str, Any],
    ) -> None:
        import winreg

        if entry.get("exists"):
            cls._write_registry(
                path,
                name,
                entry.get("value"),
                int(entry.get("type")),
            )
            return
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                path,
                0,
                winreg.KEY_SET_VALUE,
            ) as key:
                winreg.DeleteValue(key, name)
        except FileNotFoundError:
            pass

    @staticmethod
    def _call_pointer_api(size: int) -> None:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        spi = user32.SystemParametersInfoW
        spi.argtypes = [
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_void_p,
            ctypes.c_uint,
        ]
        spi.restype = ctypes.c_bool
        ctypes.set_last_error(0)
        ok = spi(
            WIN_SPI_SET_POINTER_SIZE,
            0,
            ctypes.c_void_p(size),
            WIN_SPIF_UPDATEINIFILE,
        )
        if not ok:
            error = ctypes.get_last_error()
            if error:
                raise ctypes.WinError(error)
            raise RuntimeError(
                "[UIAP-CURSOR-E204] Pointer-size API returned FALSE "
                "without a Windows error code."
            )

    def read(self) -> int:
        entry = self._read_registry(
            WIN_CURSOR_REG_PATH,
            WIN_CURSOR_REG_NAME,
            required=True,
        )
        return int(entry["value"])

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": WIN_STATE_SCHEMA,
            "cursor_base": self._read_registry(
                WIN_CURSOR_REG_PATH,
                WIN_CURSOR_REG_NAME,
                required=True,
            ),
            "accessibility": self._read_registry(
                WIN_ACCESS_REG_PATH,
                WIN_ACCESS_REG_NAME,
                required=False,
            ),
        }

    @classmethod
    def normalize_snapshot(
        cls,
        raw: dict[str, Any],
    ) -> dict[str, Any]:
        if (
            raw.get("schema") == WIN_STATE_SCHEMA
            and "cursor_base" in raw
        ):
            return raw
        # test17/test18の{size, type}形式を現在形式へ変換する。
        # 旧版の異常終了後に更新しても、保存済みサイズを復元できるようにする。
        if "size" in raw:
            size = int(raw["size"])
            value_type = int(raw.get("type", 4))
            return {
                "schema": WIN_STATE_SCHEMA,
                "cursor_base": {
                    "exists": True,
                    "value": size,
                    "type": value_type,
                },
                "accessibility": {
                    "exists": True,
                    "value": cls.slider_from_size(size),
                    "type": 4,
                },
            }
        raise RuntimeError(
            "[UIAP-CURSOR-E206] Saved cursor state format "
            "is not supported."
        )

    def current_from_snapshot(self, snapshot: dict[str, Any]) -> int:
        normalized = self.normalize_snapshot(snapshot)
        return int(normalized["cursor_base"]["value"])

    def save_snapshot(self, snapshot: dict[str, Any]) -> None:
        path = self.state_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load_snapshot(self) -> dict[str, Any]:
        path = self.state_path()
        if not path.exists():
            raise RuntimeError(
                "[UIAP-CURSOR-E208] Saved cursor state was not found."
            )
        raw = json.loads(path.read_text(encoding="utf-8"))
        return self.normalize_snapshot(raw)

    def clear_snapshot(self) -> None:
        self.state_path().unlink(missing_ok=True)

    def apply(self, value: int | float) -> int:
        import winreg

        size = self.clamp(value)
        # 2つの値を同時に更新しないと、Windows設定画面の値と実際の表示が
        # アプリ終了後に一致しなくなる場合がある。
        self._write_registry(
            WIN_CURSOR_REG_PATH,
            WIN_CURSOR_REG_NAME,
            size,
            winreg.REG_DWORD,
        )
        self._write_registry(
            WIN_ACCESS_REG_PATH,
            WIN_ACCESS_REG_NAME,
            self.slider_from_size(size),
            winreg.REG_DWORD,
        )
        self._call_pointer_api(size)
        actual = self.read()
        if actual != size:
            raise RuntimeError(
                "[UIAP-CURSOR-E205] CursorBaseSize verification "
                f"failed: expected={size} actual={actual}"
            )
        return actual

    def restore_snapshot(self, snapshot: dict[str, Any]) -> int:
        normalized = self.normalize_snapshot(snapshot)
        base = normalized["cursor_base"]
        self._restore_registry(
            WIN_CURSOR_REG_PATH,
            WIN_CURSOR_REG_NAME,
            base,
        )
        self._restore_registry(
            WIN_ACCESS_REG_PATH,
            WIN_ACCESS_REG_NAME,
            normalized["accessibility"],
        )
        self._call_pointer_api(int(base["value"]))
        actual = self.read()
        if actual != int(base["value"]):
            raise RuntimeError(
                "[UIAP-CURSOR-E207] Restore verification failed: "
                f"expected={base['value']} actual={actual}"
            )
        return actual

    def self_test(self) -> str:
        values = [
            self.clamp(80 + WIN_STEP * delta)
            for delta in (-10, -1, 1, 20)
        ]
        if values != [32, 64, 96, 256]:
            raise RuntimeError(
                "[UIAP-CURSOR-E211] Cursor mapping self-test failed."
            )
        sliders = [
            self.slider_from_size(value)
            for value in (32, 48, 80, 256)
        ]
        if sliders != [1, 2, 4, 15]:
            raise RuntimeError(
                "[UIAP-CURSOR-E212] Accessibility slider mapping failed."
            )
        migrated = self.normalize_snapshot({"size": 80, "type": 4})
        if (
            migrated["cursor_base"]["value"] != 80
            or migrated["accessibility"]["value"] != 4
        ):
            raise RuntimeError(
                "[UIAP-CURSOR-E213] Legacy state migration failed."
            )
        return "cursor mapping and state migration=PASS"


class MacCursorAPI:
    """macOSの非公開カーソル倍率APIを呼び出すctypesラッパー。"""

    def __init__(self) -> None:
        libraries: list[ctypes.CDLL] = []
        for library_path in (
            "/System/Library/Frameworks/"
            "CoreGraphics.framework/CoreGraphics",
            "/System/Library/PrivateFrameworks/"
            "SkyLight.framework/SkyLight",
        ):
            try:
                libraries.append(ctypes.CDLL(library_path))
            except OSError:
                pass
        try:
            libraries.append(ctypes.CDLL(None))
        except OSError:
            pass

        main_address = self._symbol_address(
            libraries,
            "CGSMainConnectionID",
        )
        get_address = self._symbol_address(
            libraries,
            "CGSGetCursorScale",
        )
        set_address = self._symbol_address(
            libraries,
            "CGSSetCursorScale",
        )
        if not (main_address and get_address and set_address):
            raise RuntimeError(
                "private cursor-scale symbols are unavailable"
            )

        self._main = ctypes.CFUNCTYPE(ctypes.c_int32)(main_address)
        self._get_raw = ctypes.CFUNCTYPE(
            ctypes.c_int32,
            ctypes.c_int32,
            ctypes.c_void_p,
        )(get_address)
        self._set_float = ctypes.CFUNCTYPE(
            ctypes.c_int32,
            ctypes.c_int32,
            ctypes.c_float,
        )(set_address)
        self._set_double = ctypes.CFUNCTYPE(
            ctypes.c_int32,
            ctypes.c_int32,
            ctypes.c_double,
        )(set_address)
        self.abi: str | None = None

    @staticmethod
    def _symbol_address(
        libraries: list[ctypes.CDLL],
        name: str,
    ) -> int | None:
        for library in libraries:
            try:
                function = getattr(library, name)
            except AttributeError:
                continue
            address = ctypes.cast(function, ctypes.c_void_p).value
            if address:
                return int(address)
        return None

    @property
    def connection(self) -> int:
        return int(self._main())

    @staticmethod
    def observable(value: float) -> bool:
        return (
            math.isfinite(value)
            and MAC_OBSERVED_MIN <= value <= MAC_OBSERVED_MAX
        )

    def _detect_abi(self) -> float:
        # このAPIは公開仕様ではなく、倍率の型にfloatとCGFloatの両例がある。
        # getterが書き込んだ幅を調べてから、対応するsetterの型を選択する。
        probe = ctypes.create_string_buffer(
            struct.pack("<Q", MAC_PROBE_BITS),
            8,
        )
        result = self._get_raw(
            self.connection,
            ctypes.cast(probe, ctypes.c_void_p),
        )
        if result != 0:
            raise RuntimeError(f"CGSGetCursorScale returned {result}")
        raw = bytes(probe.raw[:8])
        float_value = float(struct.unpack("<f", raw[:4])[0])
        high_word = struct.unpack("<I", raw[4:8])[0]
        double_value = float(struct.unpack("<d", raw)[0])
        if (
            high_word == MAC_PROBE_HIGH_WORD
            and self.observable(float_value)
        ):
            self.abi = "float32"
            return float_value
        if self.observable(double_value):
            self.abi = "float64"
            return double_value
        if self.observable(float_value):
            self.abi = "float32"
            return float_value
        raise RuntimeError(
            "cursor-scale ABI probe returned no observable value"
        )

    def get(self) -> float:
        if self.abi is None:
            return self._detect_abi()
        value: ctypes.c_float | ctypes.c_double
        if self.abi == "float32":
            value = ctypes.c_float(float("nan"))
        else:
            value = ctypes.c_double(float("nan"))
        result = self._get_raw(
            self.connection,
            ctypes.cast(ctypes.byref(value), ctypes.c_void_p),
        )
        current = float(value.value)
        if result != 0 or not self.observable(current):
            raise RuntimeError(
                "cursor-scale read failed "
                f"result={result} value={current!r}"
            )
        return current

    def set(self, value: float) -> None:
        if self.abi is None:
            self.get()
        if not self.observable(value):
            raise RuntimeError(
                f"refusing invalid pointer scale {value!r}"
            )
        if self.abi == "float32":
            result = self._set_float(self.connection, value)
        else:
            result = self._set_double(self.connection, value)
        if result != 0:
            raise RuntimeError(f"CGSSetCursorScale returned {result}")


class MacCursorBackend:
    """run_events()から使用するmacOS用バックエンド実装。"""

    name = "macOS"

    def __init__(self) -> None:
        self.api = MacCursorAPI()

    def state_path(self) -> Path:
        # 統合前から使っているファイル名と単一倍率値の形式を維持する。
        return (
            devkit_root()
            / ".state"
            / "04_rotary_cursor_haptic.original-scale"
        )

    @staticmethod
    def clamp(value: int | float) -> float:
        return max(MAC_MIN, min(MAC_MAX, float(value)))

    @staticmethod
    def equal(left: int | float, right: int | float) -> bool:
        return abs(float(left) - float(right)) <= MAC_COMPARE_TOLERANCE

    @staticmethod
    def format_value(value: int | float) -> str:
        return f"{float(value):.2f}"

    @staticmethod
    def next_value(current: int | float, delta: int) -> float:
        return MacCursorBackend.clamp(
            float(current) + MAC_STEP * delta
        )

    def read(self) -> float:
        return self.api.get()

    def snapshot(self) -> float:
        return self.read()

    @staticmethod
    def current_from_snapshot(snapshot: float) -> float:
        return float(snapshot)

    def save_snapshot(self, snapshot: float) -> None:
        if not self.api.observable(snapshot):
            raise RuntimeError(
                "refusing to save an invalid pointer size"
            )
        path = self.state_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{snapshot:.9g}\n", encoding="utf-8")
        os.chmod(path, 0o600)

    def load_snapshot(self) -> float:
        try:
            value = float(
                self.state_path()
                .read_text(encoding="utf-8")
                .strip()
            )
        except (OSError, ValueError) as exc:
            raise RuntimeError(
                "[UIAP-CURSOR-E205] No valid saved pointer "
                "size is available."
            ) from exc
        if not self.api.observable(value):
            raise RuntimeError(
                "saved pointer size is outside the observable range"
            )
        return value

    def clear_snapshot(self) -> None:
        self.state_path().unlink(missing_ok=True)

    def apply(self, value: int | float) -> float:
        target = self.clamp(value)
        self.api.set(target)
        actual = self.read()
        if not self.equal(target, actual):
            raise RuntimeError(
                "[UIAP-CURSOR-E216] Pointer-scale write "
                f"verification failed; requested {target:.2f}."
            )
        return actual

    def restore_snapshot(self, snapshot: float) -> float:
        self.api.set(float(snapshot))
        restored = self.read()
        if not self.equal(snapshot, restored):
            raise RuntimeError(
                "[UIAP-CURSOR-E209] Pointer-size restore "
                f"verification failed; expected {snapshot:.2f}."
            )
        return restored

    def self_test(self) -> str:
        before = self.read()
        self.api.set(before)
        after = self.read()
        if not self.equal(before, after):
            raise RuntimeError(
                "no-op write/readback mismatch: "
                f"before={before:.6g} after={after:.6g}"
            )
        return (
            f"cursor API abi={self.api.abi} "
            f"current={after:.2f} no-op-write=PASS"
        )


def create_backend():
    """実行中のOSに対応するカーソル設定バックエンドを選択する。"""
    if sys.platform == "win32":
        return WindowsCursorBackend()
    if sys.platform == "darwin":
        return MacCursorBackend()
    raise RuntimeError(
        f"[UIAP-CURSOR-E200] Unsupported platform: {sys.platform}"
    )


def recover_stale_state(backend) -> None:
    # 前回の処理で復元できなかった場合、状態ファイルは意図的に残される。
    # 新しい初期値を保存する前に、まず残っている状態を復元する。
    if not backend.state_path().exists():
        return
    print(
        "Saved cursor state from a previous interrupted run "
        "was found. Restoring it first."
    )
    snapshot = backend.load_snapshot()
    restored = backend.restore_snapshot(snapshot)
    backend.clear_snapshot()
    print(
        "Restored pointer size: "
        f"{backend.format_value(restored)}"
    )


def restore_saved_state(backend) -> int:
    snapshot = backend.load_snapshot()
    restored = backend.restore_snapshot(snapshot)
    backend.clear_snapshot()
    print(
        "Restored pointer size: "
        f"{backend.format_value(restored)}"
    )
    return 0


def run_events(dry_run: bool) -> int:
    """共通HIDループを実行する。OS固有なのはカーソル設定処理だけ。"""

    # ドライランではOSバックエンドを生成しない。
    # 設定を変えずにHIDの受信や復号を安全にカスタマイズ・確認できる。
    backend = None if dry_run else create_backend()
    original = None
    current = None
    haptic = HapticScheduler()
    if backend is not None:
        recover_stale_state(backend)
        detail = backend.self_test()
        print(f"{backend.name} {detail}")
    dev = open_device()
    try:
        if backend is not None:
            original = backend.snapshot()
            current = backend.current_from_snapshot(original)
            backend.save_snapshot(original)
            print(
                "Original pointer size: "
                f"{backend.format_value(current)}"
            )
        print("Mode: dry-run" if dry_run else "Mode: apply")
        print("Rotate the encoder. Press Ctrl+C to stop.")
        while True:
            delta = decode_delta(dev.read(64, 100))
            if delta == 0:
                pattern = haptic.take_due(time.monotonic())
                if pattern is not None:
                    trigger_haptic(dev, pattern)
                    pattern = (
                        "80ms x2"
                        if pattern == HAPTIC_NORMAL_PATTERN
                        else "250ms x1"
                    )
                    print(f"haptic={pattern} level=95", flush=True)
                continue
            direction = "CW" if delta > 0 else "CCW"
            if dry_run:
                print(f"{direction} delta={delta}", flush=True)
                continue

            assert backend is not None
            assert current is not None
            # 加速処理や非線形な変化を追加する場合は、ここでdeltaを変換するか、
            # 各バックエンドのnext_value()へ計算規則を実装する。
            target = backend.next_value(current, delta)
            if backend.equal(target, current):
                haptic.schedule(HAPTIC_LIMIT_PATTERN, time.monotonic())
                print(
                    f"{direction} limit "
                    f"{backend.format_value(current)}",
                    flush=True,
                )
                continue
            current = backend.apply(target)
            # 変更成功を保留し、最後の回転から200ms後に振動させる。
            # その前に次の入力が来た場合は、新しい結果と時刻で上書きする。
            haptic.schedule(HAPTIC_NORMAL_PATTERN, time.monotonic())
            print(
                f"{direction}: {backend.format_value(current)}",
                flush=True,
            )
    except KeyboardInterrupt:
        print("Stopping.")
    finally:
        # Ctrl+Cや実行中の多くのエラーでも元の設定へ戻せるよう、
        # 復元処理はfinally内に置く。
        try:
            dev.close()
        except Exception:
            pass
        if backend is not None and original is not None:
            try:
                restored = backend.restore_snapshot(original)
            except Exception as exc:
                print(
                    "[UIAP-CURSOR-E209] Automatic restore failed: "
                    f"{exc}",
                    file=sys.stderr,
                )
                print(
                    "Run make restore after updating the host "
                    "application.",
                    file=sys.stderr,
                )
            else:
                backend.clear_snapshot()
                print(
                    "Restored pointer size: "
                    f"{backend.format_value(restored)}"
                )
    return 0


def cursor_test() -> int:
    backend = create_backend()
    recover_stale_state(backend)
    original = backend.snapshot()
    current = backend.current_from_snapshot(original)
    target = backend.next_value(current, 1)
    if backend.equal(target, current):
        target = backend.next_value(current, -1)
    backend.save_snapshot(original)
    try:
        print(
            "Cursor test: "
            f"{backend.format_value(current)} -> "
            f"{backend.format_value(target)}"
        )
        applied = backend.apply(target)
        time.sleep(0.8)
        print(
            "Applied pointer size: "
            f"{backend.format_value(applied)}"
        )
    finally:
        restored = backend.restore_snapshot(original)
        backend.clear_snapshot()
        print(
            "Restored pointer size: "
            f"{backend.format_value(restored)}"
        )
    print(f"{backend.name} pointer-size apply/restore test: PASS")
    return 0


def protocol_self_test() -> None:
    cases = [
        ([ENCODER_REPORT_ID, 1, 221], 1),
        ([ENCODER_REPORT_ID, 255, 222], -1),
        ([ENCODER_REPORT_ID, 0, 223], 0),
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
            raise RuntimeError(
                "[UIAP-CURSOR-E210] Decode test failed: "
                f"{data} -> {actual}"
            )

    sent_reports: list[bytes] = []

    class FakeDevice:
        def send_feature_report(self, report: bytes) -> int:
            sent_reports.append(report)
            return len(report)

    trigger_haptic(FakeDevice(), HAPTIC_NORMAL_PATTERN)
    trigger_haptic(FakeDevice(), HAPTIC_LIMIT_PATTERN)
    expected = [
        bytes((HAPTIC_REPORT_ID, 95, 80, 0, 40, 0, 2)),
        bytes((HAPTIC_REPORT_ID, 95, 250, 0, 0, 0, 1)),
    ]
    if sent_reports != expected:
        raise RuntimeError(
            "[UIAP-CURSOR-E214] Haptic report self-test failed."
        )

    scheduler = HapticScheduler()
    scheduler.schedule(HAPTIC_NORMAL_PATTERN, 1.0)
    if scheduler.take_due(1.199) is not None:
        raise RuntimeError(
            "[UIAP-CURSOR-E218] Haptic delay self-test fired early."
        )
    scheduler.schedule(HAPTIC_LIMIT_PATTERN, 1.1)
    if scheduler.take_due(1.299) is not None:
        raise RuntimeError(
            "[UIAP-CURSOR-E218] Haptic reschedule self-test fired early."
        )
    if scheduler.take_due(1.301) != HAPTIC_LIMIT_PATTERN:
        raise RuntimeError(
            "[UIAP-CURSOR-E218] Haptic delay self-test did not fire."
        )


def self_test() -> int:
    protocol_self_test()
    backend = create_backend()
    detail = backend.self_test()
    print(f"Host protocol, haptic command, and {backend.name} {detail}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    # Makefileや診断スクリプトは、このCLIを外部仕様として呼び出している。
    # コマンド名を変更するときは、呼び出し側も同時に更新する。
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=[
            "list",
            "hidcheck",
            "dry-run",
            "app",
            "restore",
            "cursor-test",
            "self-test",
            "version",
        ],
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "version":
            print(
                f"uiap-haptic-host.py {VERSION} "
                f"{sys.platform} python"
            )
            return 0
        if args.command == "self-test":
            return self_test()
        if args.command == "list":
            print_devices(enumerate_devices())
            return 0
        if args.command == "hidcheck":
            require_one_device()
            print(f"{PRODUCT} HID enumeration: PASS")
            return 0
        if args.command == "restore":
            return restore_saved_state(create_backend())
        if args.command == "cursor-test":
            return cursor_test()
        return run_events(args.command == "dry-run")
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
