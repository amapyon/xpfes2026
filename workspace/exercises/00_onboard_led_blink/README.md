# 00_onboard_led_blink

UIAPduino Pro Micro CH32V003 V1.4の基板上LEDを、0.2秒点灯・0.8秒消灯で繰り返す演習です。ファームウェアとMakefileはWindows/macOS共通です。

## 検証状態

- 従来のOS別実装はWindows、macOSとも物理点滅を実機確認済み
- 共通化後の単一ファームウェアは両OSで再確認が必要

## 実行

Windows:

```text
cd /d "%UIAP_WORKSPACE%\exercises\00_onboard_led_blink"
make clean
make
make size
make flash
```

macOS:

```sh
cd "$UIAP_WORKSPACE/exercises/00_onboard_led_blink"
make clean
make
make size
make flash
```

成功条件:

- `Detected CH32V003`
- `Image written.`
- `Booting`
- LEDが0.2秒点灯・0.8秒消灯で点滅

この演習にはホスト側アプリケーションはありません。
