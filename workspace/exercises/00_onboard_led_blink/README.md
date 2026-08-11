# 00_onboard_led_blink

UIAPduino Pro Micro CH32V003 V1.4の基板上LEDを、3連フラッシュで繰り返す演習です。150ms点灯・150ms消灯を3回行い、その後1.5秒消灯します。ファームウェアとMakefileはWindows/macOS共通です。

基板上LEDは`D2 / PC0`のアクティブHighです。`High`で点灯し、`Low`で消灯します。

## 検証状態

- 従来のOS別実装はWindows、macOSとも物理点滅を実機確認済み
- 変更前の単一点滅ファームウェアはWindows、macOSとも物理点滅を実機確認済み
- 現行の3連フラッシュ版はWindows実機で動作確認済み。macOS実機は再確認が必要

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
- LEDが「短く3回点滅→1.5秒休止」を繰り返す

見た目は「パッ、パッ、パッ……」です。単発の周期点滅ではなく、3回まとまって点滅することを確認してください。これにより、工場出荷時の点滅ではなく、この演習のファームウェアが書き込まれたことを判別します。

この演習にはホスト側アプリケーションはありません。
