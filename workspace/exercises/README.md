# Exercises

4つの正式演習を配置します。すべてのファームウェアとビルド設定はWindows/macOS共通です。`02_rotary_cursor_size`と`04_rotary_cursor_haptic`は、それぞれ単一ホストが実行時にOSバックエンドを選択します。

- `00_onboard_led_blink`: ファームウェアのビルドと書き込み
- `01_macro_keyboard`: エンコーダーモジュールのGND/KEYだけを接続するHIDキーボード
- `02_rotary_cursor_size`: 同じモジュールへS1/S2/5Vを追加するHIDロータリー入力とOS別ポインターサイズホストアプリ
- `04_rotary_cursor_haptic`: `02`の回路と処理へ振動モジュールを追加し、サイズ変更時に触覚フィードバックを返す演習

操作は両OSで`make`、`make flash`、`make app`を基本とします。共通ソースは演習直下、`02`と`03`の共通ホストはそれぞれの`host/cursor_size_host.py`にあります。
