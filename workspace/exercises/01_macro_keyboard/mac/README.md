# 01_macro_keyboard

センタースイッチ付きロータリーエンコーダーモジュールの押し込み操作で、USB HIDキーボード入力を送ります。

## test10の目的

`0.1.8-test9`はmacOSでUSB Deviceとして列挙しましたが、IOHIDデバイスが生成されず、`hidutil list`に現れませんでした。test10ではDevice DescriptorとHIDクラス要求を修正し、macOSでのHID列挙と入力を検証します。

Windowsでは、test9ファームウェアを含む従来版で`AbCdE`入力を確認済みです。現在の新モジュール構成はmacOSを含む両OSで想定動作を利用者実機確認済みです。

## 配線

USBを外してから配線します。

| UIAPduino | モジュール |
|---|---|
| GND | GND |
| D8 / PC6 | S1 |
| D9 / PC7 | S2 |
| D5 / PC3 | KEY |
| 5V | 5V |

販売ページで指定されている動作電圧は5Vです。この演習で読み取る端子は`KEY`だけですが、次の演習と共通の5本を配線します。押し込み時はLowです。

## ビルドと書き込み

```sh
cd "$UIAP_WORKSPACE/exercises/01_macro_keyboard"
make clean
make
make size
make flash
```

RESETボタンを使って`1209:B803`ブートローダーモードへ入り、`make flash`を実行します。

## macOSでの列挙確認

```sh
ioreg -p IOUSB -l -w 0 > /tmp/uiap-usb.txt
grep -n -B 12 -A 24 -E 'UIAP Macro Keyboard macOS Test10|"idVendor" = 4617|"idProduct" = 49155' /tmp/uiap-usb.txt

hidutil list > /tmp/uiap-hid.txt
grep -i -E 'UIAP|0x1209|0xc003|4617|49155' /tmp/uiap-hid.txt
```

合格条件:

- `ioreg`で`bDeviceClass = 0`
- `hidutil list`でUsage Page `1`、Usage `6`
- USB Product Nameが`UIAP Macro Keyboard macOS Test10`
- USB Serial Numberが`TEST10-001`

## 入力確認

テキストエディットなど安全な入力欄を開き、英数入力にします。

- 1回押すと`AbCdE`
- 押し続けても繰り返さない
- 離して再度押すと再送する
- キーが押されたままにならない
- USB抜き差し後も再認識する

意図しない入力が続く場合はUSBケーブルを外します。コマンド入力欄、パスワード欄、ブラウザのアドレス欄では試しません。

## 一時USB識別子

```text
VID:PID: 1209:C003
Product: UIAP Macro Keyboard macOS Test10
Serial: TEST10-001
```

これらは検証用一時値であり、公開配布用の正式値ではありません。
