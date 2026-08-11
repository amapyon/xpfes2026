# 03_vibration_motor_console

PCのコンソール／ターミナルからMakeコマンドを実行し、振動モジュールを単体で動かす必須演習です。`workspace/poc/vibration_motor_hid`でWindows 11とmacOS Apple Siliconの実機確認に使用した、Vendor-defined HID Feature Report方式を演習向けに簡略化しています。

## 開始条件

先に`02_rotary_cursor_size`を完了し、エンコーダーの5本配線とカーソルサイズ変更を確認します。`02`のホストを`Ctrl+C`で終了し、USBケーブルを外してから振動モジュールを追加してください。

## 追加する部品

- ドライバー回路内蔵の5V振動モーターモジュール（`VCC`、`GND`、`IN`端子）
- ジャンパー線3本

モーター本体をGPIOへ直接接続しません。今回の回路ではVCC-GND間コンデンサーを追加しません。

## 配線

`02`のエンコーダー配線は変更せず、次の3本だけを追加します。

| UIAPduino | 振動モジュール | 用途 |
|---|---|---|
| 5V | VCC | モーター電源 |
| GND | GND | エンコーダーと共通のGND |
| D6/A2 / PC4 | IN | 振動ON/OFF制御 |

`5V`と`IN`を取り違えないでください。発熱、異臭、USB切断、連続リセットが発生した場合は直ちにUSBを外します。

## ビルドと書き込み

```text
cd ../03_vibration_motor_console
make clean
make
make size
make flash
```

書き込み直後は振動モジュールがOFFであることを確認します。USBデバイスの暫定識別子は`1209:C006`、Productは`UIAP Vibration Console`、Serialは`TEST9-001`です。

## 検証状態

- 現行版はWindows実機で書き込み、USB接続、MakeコマンドによるON/OFFとレベル変更を確認済み
- Windows向けの必須演習として完成扱い
- macOSでは元のPoC方式を確認済みだが、この演習版は実機再確認待ち
- 今回のWindows確認では詳細ログを収録していないため、各コマンドの読取り値は検証記録へ固定しない

## ターミナルから操作する

まずホストプログラムと接続を確認します。

```text
make host-doctor
make list
```

短く1回振動させます。既定は振動レベル50、0.2秒です。`LEVEL`は`1`〜`100`で指定します。

```text
make pulse
make pulse LEVEL=25
make pulse LEVEL=75 PULSE_SECONDS=0.5
```

ON/OFFを個別に確認する場合:

```text
make on LEVEL=25
make on LEVEL=75
make on LEVEL=100
make status
make off
```

レベル`1`〜`99`は500Hz PWM、レベル`100`は連続ONです。`LEVEL=100`がソフトウェア上の最大出力であり、実際の振動の強さは使用するモジュール、電源状態、取り付け方に依存します。モジュールによっては低いレベルで動き始めないことがあります。`make on`の後は必ず`make off`を実行します。停止できない、発熱する、異臭がする場合は直ちにUSBを外します。

## HID通信

ホストはFeature Report `[Report ID 1, level]`を送ります。`level=0`はPC4をLowにしてOFF、`1`〜`99`は500Hz PWM、`100`はPC4を連続Highにします。`make status`は同じFeature Reportを読み戻して現在のレベルを表示します。

## 完了条件

- `make list`で対象が1台表示される
- `make pulse`で短く振動し、自動的に停止する
- `LEVEL=25`、`75`、`100`を指定してレベルを変更できる
- `make on`、`make status`、`make off`で現在レベルを確認して停止できる
- USB接続直後は振動しない

完了後は配線を外しません。次の`04_rotary_cursor_haptic`では、振動モジュールが配線済みの状態でカーソルサイズ変更と触覚フィードバックを組み合わせます。
