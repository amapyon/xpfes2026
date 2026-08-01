# Exercises

3つの正式演習を配置します。すべてのファームウェアとビルド設定はWindows/macOS共通です。`02_rotary_cursor_size`のルートMakefileだけが、`UIAP_PLATFORM`に応じてOS固有ホストを選択します。

- `00_onboard_led_blink`: ファームウェアのビルドと書き込み
- `01_macro_keyboard`: 共通5ピンエンコーダーモジュールのKEYを使うHIDキーボード
- `02_rotary_cursor_size`: 同じモジュールのS1/S2を使うHIDロータリー入力とOS別ポインターサイズホストアプリ

操作は両OSで`make`、`make flash`、`make app`を基本とします。共通ソースは演習直下、OS固有ホストは`02_rotary_cursor_size/host/<platform>`にあります。
