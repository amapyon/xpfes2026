# 00_onboard_led_blink

UIAPduino Pro Micro CH32V003 V1.4の基板上LEDを、0.2秒点灯・0.8秒消灯で繰り返します。

検証状態:

- 過去のWindows Devkit: 実機確認済み
- `0.5.1-test14`: パッケージ静的検査のみ。Windows実機未確認

実行:

```text
cd /d "%UIAP_WORKSPACE%\exercises\00_onboard_led_blink"
make clean
make
make size
make flash
```

`make flash`はUSBブートローダー`1209:B803`を使用します。書き込み前にUIAPduinoを1台だけブートローダーモードで接続してください。
