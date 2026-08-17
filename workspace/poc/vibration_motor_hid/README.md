# vibration_motor_hid

## 目的

UIAPduino Pro Micro CH32V003 V1.4からドライバー回路内蔵の5V振動モーターモジュールを制御し、PCからUSB HID Feature Reportで振動レベルを変更できることを検証するPoCです。

このPoCは主催者向けです。ワークショップへの採用は未決定です。

構成変更後のファームウェアについて、2026-08-01にWindows 11 x64、2026-08-02にmacOS Apple Siliconでビルド、書き込み、USB HID制御、振動モーター動作を確認しました。

## 完成時の動作

- `make on 50`で振動レベル50を送る
- `make status`で現在の設定値を読む
- `make off`で停止する
- `make play`で`100:0.1,0:0.4`のパターンを繰り返す

USBはLow-SpeedのVendor-defined HIDです。アプリケーションは共有テスト用VID:PID `1209:0001`、ブートローダーは`1209:B803`です。`1209:0001`は教育目的の試作とワークショップ内テスト専用で、製品、製造、販売、再配布には使用できません。

## 使用するもの

- UIAPduino Pro Micro CH32V003 V1.4
- ドライバー回路内蔵の5V振動モーターモジュール（`VCC`、`GND`、`IN`端子）
- データ通信対応USBケーブル
- 起動済みのUIAP Devkit

モーター本体をGPIOへ直接接続しないでください。部品の定格と起動電流が不明な場合は接続しないでください。詳細は[docs/WIRING.md](docs/WIRING.md)を参照してください。

## 配線

配線を変更する前にUSBケーブルを外します。

| UIAPduino | モジュール | 用途 |
|---|---|---|
| `5V` | `VCC` | モジュール電源 |
| `GND` | `GND` | 共通GND |
| `D6/A2` | `IN` | 制御信号 |

`D6/A2`はCH32V003の`PC4`で、PWM時は`TIM1_CH4`として動作します。

## ビルドと書き込み

WindowsまたはmacOS用のUIAP Devkitを起動してから、PoCへ移動します。

```sh
cd "$UIAP_WORKSPACE/poc/vibration_motor_hid"
make doctor
make clean
make
make size
make flash
```

`make doctor`が`PoC dependencies: PASS`と`hidapi import: PASS`を表示し、`make flash`が`Image written.`と`Booting`を表示すれば次へ進みます。

## 動作確認

接続された対象デバイスを確認します。

```sh
make list
```

1台だけ表示される状態で次を実行します。

```sh
make on
make on 25
make on 75
make on 100
make status
make off
```

成功条件は、レベルに応じて振動が変わり、`status`が最後に設定した値を表示し、`off`で停止することです。

繰り返しパターンは次の形式です。

```sh
make play
make play PATTERN='100:0.05,50:0.15,0:0.8'
```

形式は`level:seconds[,level:seconds...]`です。`Ctrl+C`で終了すると、最後にレベル0を送ります。

## ファームウェアのレベル制御

- `0`: `TIM1_CH4`を無効化し、PC4をLowにする
- `1`～`99`: `TIM1_CH4`で500Hz PWMを出力する
- `100`: `TIM1_CH4`を無効化し、PC4をHighに固定する

## よくある問題

- `UIAP_PLATFORM is not set`: トップレベルの`start-uiap.cmd`または`start-uiap.command`からDevkitを起動し直す
- `Missing ch32fun`または`Missing rv003usb`: `setup`を実行して固定済み依存を準備する
- 対象デバイスが0台: アプリケーションが列挙されるまで待ち、USBケーブルと書き込み結果を確認する
- 対象デバイスが複数台: 1台だけ残して再実行する
- 振動しない: `VCC`、`GND`、`IN`、モジュール定格を確認する
- 発熱、異臭、USB切断、連続リセット: 直ちにUSBを外す

## 元に戻す方法

まず`make off`を実行し、USBケーブルを外してからモジュールの配線を外します。別の演習へ移る場合は、その演習で`make flash`を実行します。

## 構成

```text
vibration_motor_hid/
├── Makefile
├── README.md
├── POC_STATUS.txt
├── SOURCES.md
├── docs/
│   ├── VALIDATION.md
│   └── WIRING.md
├── host/
│   ├── README.md
│   └── motorctl.py
└── src/
    ├── funconfig.h
    ├── usb_config.h
    └── vibration_motor_hid.c
```

検証済み範囲と未確認事項は[docs/VALIDATION.md](docs/VALIDATION.md)を参照してください。
