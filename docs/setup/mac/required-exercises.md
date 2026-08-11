# 必須演習 — 現行構成

更新日: 2026-08-11

| 演習 | 目的 | 現在状態 |
|---|---|---|
| `00_onboard_led_blink` | ビルド・書き込み・復旧 | macOS実機合格済み |
| `01_macro_keyboard` | スイッチとUSB HID | macOS実機合格済み |
| `02_rotary_cursor_size` | エンコーダーとPC側処理 | Devkit `v0.1.2`の共通Pythonホスト版をmacOS実機で合格確認済み |
| `03_vibration_motor_console` | Makeコマンドによる振動モジュール単体制御 | 一括パターン版はWindows実機合格。macOS実機再検証対象 |
| `04_rotary_cursor_haptic` | カーソルサイズ変更と振動による触覚フィードバック | 一括パターン版はWindows実機合格。macOS実機再検証対象 |

2026-08-01の決定により、macOS版`02_rotary_cursor_size`もPythonホストアプリを使用します。USB受信は`hidapi`、カーソル設定はPython `ctypes`から非公開APIを参照します。test12の成功履歴とは別に、Devkit `v0.1.2`の共通Python実装を2026-08-11に利用者実機で合格確認しました。

`03_vibration_motor_console`は、振動なしの`02`を完了してから行います。`02`の5本配線を維持したまま、ドライバー内蔵5V振動モジュールのVCC、GND、INを追加し、VCC-GND間コンデンサーは追加しません。`make pulse LEVEL=25`、`75`、`100`で強さを比較し、`make pattern LEVEL=95 ON_MS=80 OFF_MS=40 COUNT=2`でデバイス側の繰り返しと自動停止を確認します。`make on`を使用した場合は`make status`、`make off`まで実行します。

`04_rotary_cursor_haptic`は`03`完了後、振動モジュールが配線済みの状態で行います。`02`と同じく単一のPythonホストが実行時にmacOSバックエンドを選択します。回転中はサイズだけを変更し、最後の回転から200ms後、通常変更ではレベル95で80msを2回（間隔40ms）、上限／下限では250msを1回振動することを確認します。ドライランと変更失敗時は振動しないことを合格条件とします。
