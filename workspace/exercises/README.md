# Exercises

5つの正式演習を配置します。すべてのファームウェアとビルド設定はWindows/macOS共通です。`02_rotary_cursor_size`と`04_rotary_cursor_haptic`は、それぞれ単一ホストが実行時にOSバックエンドを選択します。

- `00_onboard_led_blink`: ファームウェアのビルドと書き込み
- `01_macro_keyboard`: エンコーダーモジュールのGND/KEYだけを接続するHIDキーボード
- `02_rotary_cursor_size`: 同じモジュールへS1/S2/5Vを追加するHIDロータリー入力と共通ポインターサイズホストアプリ
- `03_vibration_motor_console`: 振動モジュールを追加し、Makeコマンドから単体でON/OFFする演習
- `04_rotary_cursor_haptic`: `02`のカーソル操作と`03`の配線・振動制御を組み合わせる演習

操作は両OSで`make`と`make flash`を基本とします。`03`は`make pulse`、`04`は`make app`で動作を確認します。共通ソースは各演習直下、ホストプログラムは各演習の`host`にあります。
