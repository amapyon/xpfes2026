# Upstream references used by this PoC

This PoC does not vendor ch32fun or rv003usb source files. It expects the UIAP Devkit fixed dependencies under `workspace/deps`.

## ch32fun

- Upstream: `cnlohr/ch32fun`
- Project-pinned commit: `1e4887e11d4bfa739ed5604524b69f5be9f9275b`
- Required PoC file: `extralibs/ws2812b_dma_spi_led_driver.h`
- Driver role: CH32V003 PC6 / SPI1 MOSI, DMA1 Channel 3, asynchronous WS2812 waveform generation

## rv003usb

- Upstream: `cnlohr/rv003usb`
- Project-pinned commit: `75d926abe89a3002020b989015eab97ce5ad0470`
- Required paths: `rv003usb/rv003usb.c`, `rv003usb/rv003usb.S`, `rv003usb/rv003usb.h`
- HID transport: Vendor-defined Feature Report over EP0

The pinned rv003usb `demo_hidapi` source also demonstrates using `ws2812b_dma_spi_led_driver.h` with `WS2812B_ALLOW_INTERRUPT_NESTING` alongside rv003usb.

## Local protocol choices

- Shared test-only VID:PID: `1209:0001` (not globally unique; workshop prototyping and testing only)
- Feature Report ID: `1`
- Report payload: 24 bytes = eight RGB triples
- LED wire order: firmware converts host RGB to WS2812B GRB

These PoC USB identifiers are not a public-distribution assignment.
