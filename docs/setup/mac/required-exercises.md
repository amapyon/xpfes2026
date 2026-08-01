# 必須演習 — test13検証

更新日: 2026-08-01

| 演習 | 目的 | 現在状態 |
|---|---|---|
| `00_onboard_led_blink` | ビルド・書き込み・復旧 | macOS実機合格済み |
| `01_macro_keyboard` | スイッチとUSB HID | macOS実機合格済み |
| `02_rotary_cursor_size` | エンコーダーとPC側処理 | test12ネイティブC版は合格。test13 Python版は再検証対象 |

2026-08-01の決定により、macOS版`02_rotary_cursor_size`もPythonホストアプリを使用します。USB受信は`hidapi`、カーソル設定はPython `ctypes`から非公開APIを参照します。test12の成功履歴は保持しますが、新Python実装の合格判定には流用しません。
