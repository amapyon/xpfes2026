# Host utility

`ws2812b8_host.py` sends a 24-byte RGB state to the UIAPduino over a Vendor-defined HID Feature Report.

Use it through the PoC Makefile:

```sh
make app on
make app off
make app demo
make app 1:255,255,255
make app 1:255,255,255,8:255,128,0
make app status
make list
make doctor
```

The UIAP Devkit bundled Python and hidapi are expected. Do not create a separate venv for this PoC.

On macOS, launch the Devkit with `start-uiap.command`. `make doctor` verifies that
the bundled hidapi can be imported and that Python is running natively as Apple
Silicon `arm64` before a device is accessed.

`make app demo` is a visual test. It lights LEDs 1 through 8 one at a time, then
shows red, green, and blue on all LEDs at brightness levels 16, 64, 128, and 255.
It finishes with all LEDs off; pressing Ctrl+C also attempts to turn them off.
Human visual validation passed on Windows 11 x64 on 2026-08-16. The demo remains
to be visually validated on macOS.
