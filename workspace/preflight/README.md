# UIAPduino HID Preflight

UIAPduino Pro Micro CH32V003 V1.4のUSB通信を、演習開始前に確認するための事前診断です。専用ファームウェアを書き込み、PCとのVendor-defined HID通信が正常に往復できることを確認します。

## 確認する項目

- USB HIDデバイスとしての列挙（VID `1209`、PID `D003`）
- ランダムな値を使ったPC → UIAPduino → PCの往復通信
- 通信プロトコルとファームウェアのバージョン
- 対象ボード名
- CH32V003のMCU ID

この診断は、LED、ロータリーエンコーダーなど演習ごとの外付け部品は確認しません。

## 検証状態

2026-08-05にWindows実機で、ビルド、USBブートローダー経由の書き込み、診断用HIDへの再列挙、PCとの双方向通信、バージョン、ボード名、MCU IDを確認済みです。すべての検査が`PASS`し、minichlinkとHID診断が表示したMCU IDも一致しました。

同日、macOS実機でも事前診断が正常に動作することを確認済みです。これにより、WindowsとmacOSの両方で実機確認済みです。詳細は[検証結果](../../docs/project/70_VALIDATION_RESULTS.md)を参照してください。

## 実行方法

先にDevkitルートの起動ファイルから開発環境を開始し、`setup`と`doctor`を完了してください。UIAPduinoをUSBで接続した状態で、次を実行します。

Windows:

```console
cd /d "%UIAP_WORKSPACE%\preflight"
make
make flash
make preflight
```

macOS:

```console
cd "$UIAP_WORKSPACE/preflight"
make
make flash
make preflight
```

`make flash`の後、USBデバイスが再接続されてから`make preflight`を実行してください。成功時は各項目に`[PASS]`が表示され、最後に次のように表示されます。

```text
RESULT: PASS
UIAPduino is operating as a Vendor-defined USB HID device.
```

終了コードは成功時が`0`、失敗時が非ゼロです。

## コマンド

| コマンド | 内容 |
|---|---|
| `make` | 診断用ファームウェアをビルド |
| `make flash` | UIAPduinoのUSBブートローダー経由で書き込み |
| `make preflight` | PCからHID事前診断を実行 |
| `make size` | ファームウェアサイズを表示 |
| `make clean` | ビルド生成物を削除 |
| `make help` | コマンド一覧を表示 |

## 失敗した場合

- `hidapi could not be imported`: Devkitルートへ戻り、`setup`と`doctor`を再実行します。
- `preflight HID device ... was not found`: USBケーブルと接続を確認し、`make flash`を再実行します。書き込み直後は再列挙を少し待ちます。
- `expected one ... found ...`: 診断用ファームウェアを書き込んだUIAPduinoを1台だけ接続します。
- `Protocol version`、`Firmware version`、`Board target`が`FAIL`: `preflight_hid.c`と`host/preflight_hid.py`の組み合わせが一致していません。同じDevkitに含まれるファイルで再ビルド・再書き込みします。
- `response ... timed out`: USBハブを外してPCへ直接接続し、再書き込み後に試します。

改善しない場合は、Devkitルートで`report`を実行し、出力を保存してください。

## 開発者向け情報

- `preflight_hid.c`: CH32V003用の診断ファームウェア
- `usb_config.h`: Vendor-defined HIDのUSB Descriptor
- `host/preflight_hid.py`: hidapiを使用するPC側診断
- `Makefile`: 両OS共通のビルド、書き込み、診断入口

Feature ReportはReport IDを含む8バイト固定です。PC側診断が期待する現在の組み合わせは、プロトコル`1.2`、ファームウェア`1.0.2`、ボード`UIAPduino Pro Micro CH32V003 V1.4`です。これらを変更するときは、ファームウェアとPC側診断を同時に更新してください。

`.bin`、`.elf`、`.hex`、`.lst`、`.map`と`funconfig.h`はビルド生成物です。ソース管理や配布元には含めません。
