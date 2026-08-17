# Upstream references used by this PoC

This PoC does not vendor ch32fun or rv003usb. It uses the fixed dependencies under `workspace/deps`.

## ch32fun

- Upstream: `cnlohr/ch32fun`
- Project-pinned commit: `1e4887e11d4bfa739ed5604524b69f5be9f9275b`
- Used for: CH32V003 startup, register definitions, linker script, and timing helpers

## rv003usb

- Upstream: `cnlohr/rv003usb`
- Project-pinned commit: `75d926abe89a3002020b989015eab97ce5ad0470`
- Used for: Low-Speed USB device implementation and HID Feature Reports over endpoint 0

## Local protocol choices

- Shared test-only VID:PID: `1209:0001` (not globally unique; workshop prototyping and testing only)
- Feature Report ID: `1`
- Payload: one byte, vibration level `0`～`100`
- PWM: UIAPduino `D6/A2` / CH32V003 `PC4` / `TIM1_CH4`, 500Hz

The USB identifier is temporary and is not an assignment for public distribution or a product.
