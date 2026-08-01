# Exercises

3つの正式演習を配置します。`01_macro_keyboard`はWindows/macOS共通実装です。OS固有処理がある演習だけ、ルートMakefileが`UIAP_PLATFORM`に応じて`win/`または`mac/`を選択します。

- `00_onboard_led_blink`: ファームウェアのビルドと書き込み
- `01_macro_keyboard`: 共通5ピンエンコーダーモジュールのKEYを使うHIDキーボード
- `02_rotary_cursor_size`: 同じモジュールのS1/S2を使うHIDロータリー入力とOS別ポインターサイズホストアプリ

操作は両OSで`make`、`make flash`、`make app`を基本とします。共通ソースは演習直下、OS固有ソースは対応するプラットフォームのディレクトリにあります。
