# Exercises

3つの正式演習を配置します。すべてのファームウェアとビルド設定はWindows/macOS共通です。`02_rotary_cursor_size`は単一ホストが実行時にOSバックエンドを選択します。

- `00_onboard_led_blink`: ファームウェアのビルドと書き込み
- `01_macro_keyboard`: エンコーダーモジュールのGND/KEYだけを接続するHIDキーボード
- `02_rotary_cursor_size`: 同じモジュールへS1/S2/5Vを追加するHIDロータリー入力と共通ポインターサイズホストアプリ

操作は両OSで`make`、`make flash`、`make app`を基本とします。共通ソースは演習直下、共通ホストは`02_rotary_cursor_size/host/cursor_size_host.py`にあります。
