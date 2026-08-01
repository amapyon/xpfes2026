# 00_onboard_led_blink

基板上LEDを0.2秒点灯、0.8秒消灯で繰り返します。ビルド、USBブートローダー書き込み、復旧確認の基準演習です。

## 検証状態

- macOS Apple Silicon: `0.1.7-test8`でビルド、書き込み、ブート、物理点滅まで確認済み
- `0.2.2-test13`: 回帰検証対象

## 実行

```sh
make clean
make
make size
make flash
```

## 成功条件

- `Detected CH32V003`
- `Image written.`
- `Booting`
- LEDが0.2秒点灯、0.8秒消灯で点滅

書き込み時は、リセットボタンを押したままUSBを接続し、ボタンを離してから直ちに`make flash`を実行します。
