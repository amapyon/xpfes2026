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

書き込み直後は振動モジュールがOFFであることを確認します。USBデバイスの共有テスト用識別子は`1209:0001`、Productは`UIAP Vibration Console`、Serialは`TEST9-001`です。`1209:0001`は世界で一意ではなく、教育目的の試作とワークショップ内テスト専用です。製品、製造、販売、再配布には使用しません。

## 検証状態

- 変更前のレベル単独レポート版は、Windows/macOS実機でON/OFFとレベル変更を確認済み
- 現行の一括パターンレポート版は、Windows実機で想定動作を確認済み。macOS実機で再確認が必要
- 今回のWindows確認では詳細ログを収録していないため、各コマンドの読取り値は検証記録へ固定しない

## ターミナルから操作する

まずホストプログラムと接続を確認します。

```text
make host-doctor
make hidcheck
make list
```

`make hidcheck`では次の形式で表示されます。`Product:`が`UIAP Vibration Console`であり、最終行にも同じ名称が表示されることを確認してください。

```text
Matching devices: 1
[0] VID:PID=1209:0001
  Product: UIAP Vibration Console
  Serial: TEST9-001
UIAP Vibration Console HID enumeration: PASS
```

Product名が異なる場合は次へ進まず、この演習のファームウェアを書き込んだか確認します。

短く1回振動させます。既定は振動レベル50、0.2秒です。`LEVEL`は`1`〜`100`で指定します。

```text
make pulse
make pulse LEVEL=25
make pulse LEVEL=75 PULSE_SECONDS=0.5
```

`make pulse`はLEVELと時間を1回のFeature Reportで送り、待機せず終了します。指定時間後の停止はデバイス側が行います。

LEVEL、ON時間、OFF時間、回数を指定する場合:

```text
make pattern LEVEL=95 ON_MS=80 OFF_MS=40 COUNT=2
make pattern LEVEL=95 ON_MS=250 OFF_MS=0 COUNT=1
```

`ON_MS`と`OFF_MS`は`0`〜`5000`ms、`COUNT`は`1`〜`255`です。有限パターンでは`ON_MS`を1ms以上にします。

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

ホストはFeature Report `[Report ID 1, level, on_ms_lo, on_ms_hi, off_ms_lo, off_ms_hi, count]`を1回送ります。時間はリトルエンディアンの16ビット整数です。デバイスは受信したパターンを500Hz PWMで実行し、指定回数後に自動停止します。

- `level=0`: 即時停止
- `count=0`かつ`level>0`: `make on`用の連続動作
- `count>=1`: 指定したON/OFF時間と回数を実行して自動停止
- `level=1`〜`99`: 500Hz PWM
- `level=100`: 連続High

`make status`は同じFeature Reportを読み戻し、現在の出力状態と最後に指定したパターンを表示します。

## 完了条件

- `make list`で対象が1台表示される
- `make pulse`で短く振動し、自動的に停止する
- `make pattern LEVEL=95 ON_MS=80 OFF_MS=40 COUNT=2`で2回振動し、自動的に停止する
- `LEVEL=25`、`75`、`100`を指定してレベルを変更できる
- `make on`、`make status`、`make off`で現在レベルを確認して停止できる
- USB接続直後は振動しない

完了後は配線を外しません。次の`04_rotary_cursor_haptic`では、振動モジュールが配線済みの状態でカーソルサイズ変更と触覚フィードバックを組み合わせます。
