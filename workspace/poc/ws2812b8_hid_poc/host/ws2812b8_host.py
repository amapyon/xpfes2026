#!/usr/bin/env python3
"""Host controller for the UIAP WS2812B8 HID PoC."""

from __future__ import annotations

import re
import platform
import sys
import time
from dataclasses import dataclass
from typing import Iterable, Sequence

VID = 0x1209
PID = 0xD008
PRODUCT = "UIAP WS2812B8 PoC"
REPORT_ID = 0x01
LED_COUNT = 8
REPORT_PAYLOAD_SIZE = LED_COUNT * 3
REPORT_TOTAL_SIZE = 1 + REPORT_PAYLOAD_SIZE
SAFE_ON_VALUE = 64
DEMO_INDIVIDUAL_SECONDS = 0.6
DEMO_BRIGHTNESS_SECONDS = 0.8
DEMO_BRIGHTNESS_LEVELS = (16, 64, 128, 255)

# Conservative, simple workshop estimate: 20 mA per full-scale color channel.
EST_MA_PER_CHANNEL = 20.0
CURRENT_WARNING_MA = 400.0


@dataclass(frozen=True)
class RGB:
    r: int
    g: int
    b: int


ASSIGNMENT = re.compile(r"(\d+):(\d+),(\d+),(\d+)(?:,|$)")


def usage() -> str:
    return """Usage:
  make app on
  make app off
  make app status
  make app demo
  make app 1:255,255,255
  make app 8:255,128,0
  make app 1:255,255,255,8:255,128,0
  make app 1:255,255,255,7:0,128,255,8:255,128,0

Rules:
  LED number: 1..8
  R,G,B:      0..255
  Unspecified LEDs are OFF.
  'on' lights all 8 LEDs white at RGB 64,64,64 as a conservative USB-power default.
  'demo' lights LEDs 1..8 individually, then shows red, green, and blue brightness steps.
"""


def parse_spec(spec: str) -> list[RGB]:
    spec = spec.strip()
    leds = [RGB(0, 0, 0) for _ in range(LED_COUNT)]

    if spec == "off":
        return leds
    if spec == "on":
        return [RGB(SAFE_ON_VALUE, SAFE_ON_VALUE, SAFE_ON_VALUE) for _ in range(LED_COUNT)]
    if spec == "status":
        raise ValueError("status is a query, not an LED state")
    if not spec:
        raise ValueError("no LED specification was supplied")

    pos = 0
    seen = False
    while pos < len(spec):
        match = ASSIGNMENT.match(spec, pos)
        if match is None:
            raise ValueError(f"invalid LED specification near: {spec[pos:]!r}")

        led_no, r, g, b = (int(v) for v in match.groups())
        if not 1 <= led_no <= LED_COUNT:
            raise ValueError(f"LED number must be 1..{LED_COUNT}: {led_no}")
        for name, value in (("R", r), ("G", g), ("B", b)):
            if not 0 <= value <= 255:
                raise ValueError(f"{name} must be 0..255: {value}")

        leds[led_no - 1] = RGB(r, g, b)
        seen = True
        pos = match.end()

    if not seen:
        raise ValueError("no LED assignments were found")
    return leds


def encode_report(leds: Sequence[RGB]) -> list[int]:
    if len(leds) != LED_COUNT:
        raise ValueError(f"expected {LED_COUNT} LEDs")
    report = [REPORT_ID]
    for led in leds:
        report.extend((led.r, led.g, led.b))
    if len(report) != REPORT_TOTAL_SIZE:
        raise AssertionError("internal report length mismatch")
    return report


def decode_report(data: Sequence[int]) -> list[RGB]:
    values = list(data)
    if len(values) >= REPORT_TOTAL_SIZE and values[0] == REPORT_ID:
        payload = values[1:REPORT_TOTAL_SIZE]
    elif len(values) >= REPORT_PAYLOAD_SIZE:
        # Some Python HID wrappers omit the report ID on reads.
        payload = values[:REPORT_PAYLOAD_SIZE]
    else:
        raise ValueError(f"short Feature Report: {len(values)} bytes")

    return [RGB(*payload[i:i + 3]) for i in range(0, REPORT_PAYLOAD_SIZE, 3)]


def estimated_led_current_ma(leds: Iterable[RGB]) -> float:
    total = sum(led.r + led.g + led.b for led in leds)
    return total * EST_MA_PER_CHANNEL / 255.0


def print_state(leds: Sequence[RGB], prefix: str = "") -> None:
    for index, led in enumerate(leds, 1):
        print(f"{prefix}{index}: {led.r},{led.g},{led.b}")
    estimate = estimated_led_current_ma(leds)
    print(f"Estimated LED current (conservative model): {estimate:.0f} mA")
    if estimate > CURRENT_WARNING_MA:
        print(
            f"WARNING: estimated LED current exceeds {CURRENT_WARNING_MA:.0f} mA. "
            "Verify USB power capacity, wiring, LED variant, and temperature.",
            file=sys.stderr,
        )


def import_hid():
    try:
        import hid  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "hidapi could not be imported. Start the UIAP Devkit environment and run setup/doctor."
        ) from exc
    return hid


def platform_doctor() -> int:
    self_test()
    hid_module = import_hid()
    machine = platform.machine()
    if sys.platform == "darwin" and machine != "arm64":
        raise RuntimeError(
            f"macOS host must run natively on Apple Silicon arm64; detected {machine or 'unknown'}"
        )
    version = getattr(hid_module, "__version__", "unknown")
    print(f"Host platform: {sys.platform} / {machine or 'unknown'}")
    print(f"Python: {platform.python_version()}")
    print(f"hidapi import: PASS (version {version})")
    return 0


def matching_devices(hid_module):
    devices = list(hid_module.enumerate(VID, PID))
    exact = [d for d in devices if d.get("product_string") == PRODUCT]
    return exact if exact else devices


def print_devices() -> int:
    hid_module = import_hid()
    devices = matching_devices(hid_module)
    print(f"Matching devices: {len(devices)}")
    for index, device in enumerate(devices):
        print(f"[{index}] VID:PID={VID:04X}:{PID:04X}")
        print(f"  Product: {device.get('product_string')}")
        print(f"  Serial: {device.get('serial_number')}")
        print(f"  Path: {device.get('path')}")
    return 0 if devices else 1


def open_one_device():
    hid_module = import_hid()
    devices = matching_devices(hid_module)
    if not devices:
        raise RuntimeError(f"{PRODUCT} ({VID:04X}:{PID:04X}) was not found")
    if len(devices) != 1:
        raise RuntimeError(
            f"{len(devices)} matching devices found. Connect exactly one WS2812B8 PoC device."
        )

    path = devices[0].get("path")
    if path is None:
        raise RuntimeError("HID device path is unavailable")

    if hasattr(hid_module, "device"):
        dev = hid_module.device()
        dev.open_path(path)
        return dev

    # Compatibility with wrappers exposing the newer class-style API.
    if hasattr(hid_module, "Device"):
        return hid_module.Device(path=path)

    raise RuntimeError("unsupported Python hidapi API")


def send_state(leds: Sequence[RGB]) -> None:
    report = encode_report(leds)
    dev = open_one_device()
    try:
        send_state_to_open_device(dev, report)
    finally:
        dev.close()


def send_state_to_open_device(dev, report: Sequence[int]) -> None:
    result = dev.send_feature_report(bytes(report))
    if result is not None and result < 0:
        raise RuntimeError("send_feature_report returned an error")


def demo_steps() -> list[tuple[str, list[RGB], float]]:
    steps: list[tuple[str, list[RGB], float]] = []
    for led_index in range(LED_COUNT):
        leds = [RGB(0, 0, 0) for _ in range(LED_COUNT)]
        leds[led_index] = RGB(SAFE_ON_VALUE, SAFE_ON_VALUE, SAFE_ON_VALUE)
        steps.append(
            (
                f"Individual LED {led_index + 1}/{LED_COUNT}: white {SAFE_ON_VALUE}",
                leds,
                DEMO_INDIVIDUAL_SECONDS,
            )
        )

    channels = (
        ("Red", lambda value: RGB(value, 0, 0)),
        ("Green", lambda value: RGB(0, value, 0)),
        ("Blue", lambda value: RGB(0, 0, value)),
    )
    for channel_name, color_for_value in channels:
        for value in DEMO_BRIGHTNESS_LEVELS:
            color = color_for_value(value)
            steps.append(
                (
                    f"{channel_name} brightness {value}/255: all LEDs",
                    [color for _ in range(LED_COUNT)],
                    DEMO_BRIGHTNESS_SECONDS,
                )
            )
    return steps


def run_demo() -> None:
    off = [RGB(0, 0, 0) for _ in range(LED_COUNT)]
    dev = open_one_device()
    print("Visual demo started. Confirm each LED and each RGB brightness step by eye.")
    try:
        send_state_to_open_device(dev, encode_report(off))
        for label, leds, duration in demo_steps():
            print(label, flush=True)
            send_state_to_open_device(dev, encode_report(leds))
            time.sleep(duration)
    finally:
        try:
            send_state_to_open_device(dev, encode_report(off))
            print("Demo finished. All LEDs are OFF.")
        finally:
            dev.close()


def read_state() -> list[RGB]:
    dev = open_one_device()
    try:
        data = dev.get_feature_report(REPORT_ID, REPORT_TOTAL_SIZE)
    finally:
        dev.close()
    return decode_report(data)


def self_test() -> int:
    tests = {
        "off": [RGB(0, 0, 0)] * 8,
        "1:255,255,255": [RGB(255, 255, 255)] + [RGB(0, 0, 0)] * 7,
        "8:255,128,0": [RGB(0, 0, 0)] * 7 + [RGB(255, 128, 0)],
        "1:255,255,255,8:255,128,0": [RGB(255, 255, 255)]
        + [RGB(0, 0, 0)] * 6
        + [RGB(255, 128, 0)],
    }
    for spec, expected in tests.items():
        actual = parse_spec(spec)
        if actual != expected:
            raise AssertionError(f"parse mismatch for {spec}: {actual!r}")
        report = encode_report(actual)
        if decode_report(report) != expected:
            raise AssertionError(f"report round-trip mismatch for {spec}")

    all_on = parse_spec("on")
    if any(led != RGB(SAFE_ON_VALUE, SAFE_ON_VALUE, SAFE_ON_VALUE) for led in all_on):
        raise AssertionError("on command default mismatch")

    invalid = ["0:1,2,3", "9:1,2,3", "1:256,0,0", "1:1,2", "garbage"]
    for spec in invalid:
        try:
            parse_spec(spec)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid specification accepted: {spec}")

    steps = demo_steps()
    if len(steps) != LED_COUNT + 3 * len(DEMO_BRIGHTNESS_LEVELS):
        raise AssertionError("demo step count mismatch")
    for led_index, (_, leds, _) in enumerate(steps[:LED_COUNT]):
        expected = [RGB(0, 0, 0) for _ in range(LED_COUNT)]
        expected[led_index] = RGB(SAFE_ON_VALUE, SAFE_ON_VALUE, SAFE_ON_VALUE)
        if leds != expected:
            raise AssertionError(f"individual demo mismatch for LED {led_index + 1}")

    expected_colors = [
        RGB(value, 0, 0) for value in DEMO_BRIGHTNESS_LEVELS
    ] + [
        RGB(0, value, 0) for value in DEMO_BRIGHTNESS_LEVELS
    ] + [
        RGB(0, 0, value) for value in DEMO_BRIGHTNESS_LEVELS
    ]
    actual_colors = [leds[0] for _, leds, _ in steps[LED_COUNT:]]
    if actual_colors != expected_colors:
        raise AssertionError("RGB brightness demo sequence mismatch")

    print("Host parser/report self-test: PASS")
    return 0


def main(argv: Sequence[str]) -> int:
    if len(argv) == 2 and argv[1] == "--self-test":
        return self_test()
    if len(argv) == 2 and argv[1] == "--doctor":
        try:
            return platform_doctor()
        except RuntimeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
    if len(argv) == 2 and argv[1] == "--list":
        return print_devices()
    if len(argv) != 2:
        print(usage(), file=sys.stderr)
        return 2

    spec = argv[1].strip()
    if spec == "demo":
        try:
            run_demo()
        except KeyboardInterrupt:
            print("Demo interrupted.", file=sys.stderr)
            return 130
        except (RuntimeError, OSError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        return 0
    if spec == "status":
        try:
            leds = read_state()
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        print_state(leds)
        return 0

    try:
        leds = parse_spec(spec)
        print_state(leds)
        send_state(leds)
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("LED state sent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
