# Exercises

3つの正式演習を配置します。各演習のルートMakefileは`UIAP_PLATFORM`に応じて`win/`または`mac/`を選択します。

- `00_onboard_led_blink`: ファームウェアのビルドと書き込み
- `01_macro_keyboard`: HIDキーボードのビルド、書き込み、ホスト列挙
- `02_rotary_cursor_size`: HIDロータリー入力とOS別ポインターサイズホストアプリ

操作は両OSで`make`、`make flash`、`make app`を基本とします。OS固有ソースを直接編集する場合は、現在のプラットフォームに対応するディレクトリを編集します。
