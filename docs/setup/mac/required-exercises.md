# 必須演習 — 現行構成

更新日: 2026-08-11

| 演習 | 目的 | 現在状態 |
|---|---|---|
| `00_onboard_led_blink` | ビルド・書き込み・復旧 | macOS実機合格済み |
| `01_macro_keyboard` | スイッチとUSB HID | macOS実機合格済み |
| `02_rotary_cursor_size` | エンコーダーとPC側処理 | test12ネイティブC版は合格。test13 Python版は再検証対象 |
| `04_rotary_cursor_haptic` | カーソルサイズ変更と振動による触覚フィードバック | 2026-08-11追加。Windows/macOSとも実機再検証対象 |

2026-08-01の決定により、macOS版`02_rotary_cursor_size`もPythonホストアプリを使用します。USB受信は`hidapi`、カーソル設定はPython `ctypes`から非公開APIを参照します。test12の成功履歴は保持しますが、新Python実装の合格判定には流用しません。

`04_rotary_cursor_haptic`は、振動なしの`02`を完了してから行います。`02`と同じく単一のPythonホストが実行時にmacOSバックエンドを選択します。`02`の5本の配線を維持したまま、ドライバー内蔵5V振動モジュールのVCC、GND、INだけを追加し、VCC-GND間コンデンサーは追加しません。ポインターサイズの変更確認後だけ約60ms振動し、上限／下限、ドライラン、変更失敗時は振動しないことを合格条件とします。
