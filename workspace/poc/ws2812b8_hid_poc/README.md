# WS2812B 8-LED HID PoC

UIAPduino Pro Micro CH32V003 V1.4から、直列接続された8個のWS2812B / NeoPixel系LEDを制御する主催者向けPoCです。

PCからVendor-defined USB HID Feature Reportで8灯分のRGB値を送り、CH32V003側ではch32funの`ws2812b_dma_spi_led_driver.h`を利用してSPI1 + DMAでLED波形を生成します。

## 検証状態

- ソース作成: 済み
- ホスト側コマンド解析セルフテスト: Windowsで確認済み
- ファームウェア実ビルド: Windowsで確認済み
- UIAPduinoへの書き込み: Windowsで確認済み
- USB HID列挙: Windowsで確認済み
- WS2812B物理点灯: Windowsで修正版を確認済み
- Windows 11 x64実機: 確認済み
- macOS Apple Silicon対応実装: 済み
- macOS Apple Silicon実機: 確認待ち
- 参加者向け演習としての採用: 未決定

一段階の成功を後続段階の成功として扱わないでください。

## ZIPの配置

このZIPは`workspace`直下で展開する想定です。

```text
workspace/
└── poc/
    └── ws2812b8_hid_poc/
```

## 使用ピン

WS2812Bデータ出力は次を使用します。

```text
D8 / MOSI / PC6
```

ch32funのWS2812 DMA/SPIドライバはCH32V003でPC6を使用します。

**注意:** 必須演習`02_rotary_cursor_size`もD8 / PC6を使用します。同じUIAPduino上で同時使用しないでください。

## 推奨配線

配線変更前にUSBケーブルを外してください。

| UIAPduino | 接続先 | 用途 |
|---|---|---|
| +5V | WS2812B VCC / +5V | LED電源 |
| GND | WS2812B GND | 共通GND |
| D8 / PC6 | レベルシフタ入力 | WS2812データ |
| レベルシフタ出力 | 330Ω程度を介してDIN | データ保護 |

5V駆動WS2812Bへ確実にHighを認識させるため、74AHCT125などの5V駆動AHCT系バッファによるレベル変換を推奨します。LED電源入口の近くにバルクコンデンサを配置してください。

実際に使用する8灯部品の回路、内蔵抵抗・コンデンサ、信号入力仕様が確認できる場合は、その仕様を優先してください。

## 電源上の注意

8灯を高輝度の白で同時点灯するとUSBからの電流が大きくなります。このPoCでは、

```text
make app on
```

を「全8灯をRGB 64,64,64で白点灯」としています。これは最大輝度を意味しません。

個別指定では0～255を許可します。ホストアプリはRGB値から保守的なLED電流推定値を表示し、400mAを超える場合に警告します。これは実測値ではありません。

発熱、異臭、USB切断、UIAPduinoのリセットが起きた場合は直ちにUSBを外してください。

## 必要な依存関係

Devkitの次を使用します。

```text
workspace/deps/ch32fun
workspace/deps/rv003usb
runtime/bin/minichlink
runtime/python
```

このPoCでは追加でch32funの次のファイルが必要です。

```text
workspace/deps/ch32fun/extralibs/ws2812b_dma_spi_led_driver.h
```

参加者向けch32funサブセットにこのファイルが入っていない場合、PoC検証用の許可リストへ追加してから再生成してください。上流ツリー全体を手作業で上書きしないでください。

## ビルド

`start-uiap.cmd`または`start-uiap.command`からDevkit環境を開き、このPoCへ移動します。

Windows:

```text
cd /d "%UIAP_WORKSPACE%\poc\ws2812b8_hid_poc"
make check-deps
make clean
make
```

macOS:

```sh
cd "$UIAP_WORKSPACE/poc/ws2812b8_hid_poc"
make check-deps
make clean
make
```

macOSでは、先にDevkitルートの`start-uiap.command`から環境を開いてください。
初回セットアップがまだの場合は`setup`、書き込みツールがまだの場合は
主催者環境で`build-minichlink`を実行します。PoCの事前診断は次で行えます。

```sh
make doctor
```

この診断では、依存ソース、ホスト側のレポート処理、同梱Pythonからの
hidapi読み込み、Apple Silicon `arm64`でのネイティブ実行を確認します。

## macOS実機確認

macOS側では、Windowsで動作確認したものと同じファームウェアソースと
Vendor-defined HID Feature Reportを使用します。macOS向けには、IOHIDFamilyが
接続時に行うHID Idle照会への応答と、Apple Siliconネイティブ実行の診断を
追加しています。

次の順に確認してください。

```sh
make doctor
make clean
make
make flash
make list
make app off
make app 1:255,0,0
make app 8:0,255,0
make app on
make app status
make app off
```

成功条件は次のとおりです。

- `make doctor`が依存関係、Python、hidapi、`arm64`をすべてPASSとする
- `make list`がProduct `UIAP WS2812B8 PoC`を1台表示する
- 個別指定では指定したLEDだけが指定色で点灯する
- `make app on`で8灯、`make app off`で全消灯する
- `make app status`が最後に送信したRGB状態を返す
- USBを抜き差ししても再列挙できる

macOS実機でこの一連の確認が完了するまでは、macOS確認済みとは扱いません。

## 書き込み

UIAPduinoをUSBブートローダーモード`1209:B803`にして実行します。

```sh
make flash
```

## HID仕様

| 項目 | 値 |
|---|---|
| USB | USB 2.0 Low-Speed |
| Usage Page | Vendor-defined `0xFF00` |
| Usage | `0x0008` |
| Report | Feature Report |
| Report ID | `1` |
| Payload | 24 bytes |
| 内容 | LED1～LED8のRGB、各3 byte |
| PoC VID:PID | `1209:D008` |
| Product | `UIAP WS2812B8 PoC` |

`1209:D008`はこのPoC内だけの暫定値です。公開配布用VID:PIDとして決定したものではありません。

## 操作

### すべて点灯

8灯を安全側の白`64,64,64`で点灯します。

```sh
make app on
```

### すべて消灯

```sh
make app off
```

### 起点の1灯だけ白

```sh
make app 1:255,255,255
```

### 一番遠いLEDだけオレンジ

```sh
make app 8:255,128,0
```

### 2灯

```sh
make app 1:255,255,255,8:255,128,0
```

### 3灯

```sh
make app 1:255,255,255,7:0,128,255,8:255,128,0
```

指定しなかったLEDは消灯します。同じLED番号を複数回指定した場合は最後の指定が有効です。

### 現在状態

```sh
make app status
```

### HID列挙

```sh
make list
```

### ホスト側セルフテスト

```sh
make doctor
```

## コマンド形式

```text
LED番号:R,G,B
```

範囲:

```text
LED番号 = 1～8
R = 0～255
G = 0～255
B = 0～255
```

複数LEDは空白を入れず、カンマで続けます。

```text
1:255,0,0,4:0,255,0,8:0,0,255
```

## 実装メモ

- PC側Feature ReportはRGB順です。
- WS2812Bへの物理送信時だけファームウェアでGRB順へ変換します。
- ch32funのDMA/SPIドライバを使用するため、出力ピンはPC6固定です。
- `WS2812B_ALLOW_INTERRUPT_NESTING`を有効にし、rv003usbとDMA割り込みを共存させます。
- WS2812Bの波形生成中に長時間USB割り込みを止めるbit-bang方式は使用していません。
- macOSのIOHIDFamilyによる接続時照会に備え、HID `GET_IDLE` / `SET_IDLE`へ応答します。

## 最初の実機検証順序

1. `make check-deps`
2. `make clean`
3. `make`
4. `make flash`
5. `make list`
6. `make app off`
7. `make app 1:255,0,0`
8. `make app 1:0,255,0`
9. `make app 1:0,0,255`
10. `make app 8:255,128,0`
11. `make app 1:255,255,255,8:255,128,0`
12. `make app on`
13. USB抜き差し後に再度`make list`と点灯確認

色順が想定と異なる場合は、まずLED部品が本当にWS2812B互換のGRB順かを確認してください。ファームウェア側の色順を推測で変更しないでください。


## 既知問題修正: 8灯のうち先頭6灯までしか安定しない

2026-08-01の初回実機試験では、旧版の`DMALEDS=16`で次の症状を確認しました。

- `make app on`: 起点から6灯だけ点灯
- `make app off`: 起点LEDが残灯
- LED 1、2の個別指定: 不正な点灯
- LED 3～6: 期待どおり
- LED 7、8: 点灯しない

原因は、ch32funのWS2812 DMA/SPIドライバにおける`DMALEDS`の意味を実LED数相当と誤認していたことです。非`WSRAW`モードではDMAバッファに保持できるLED時間枠は`DMALEDS / 2`です。さらに送信先頭にはリセット用Low期間が必要です。旧設定`DMALEDS=16`では8枠しかなく、先頭のリセット2枠を除くと初回バッファへLED 1～6までしか入りません。

修正版では次に変更しています。

```c
#define DMALEDS 32
```

これにより16枠を確保し、リセット2枠、LED 1～8、末尾のLow期間を同一の初回DMAバッファへ収めます。Windows 11 x64では、この変更後の実機動作を確認済みです。macOS Apple Siliconでは未確認です。

### 修正版の再試験

書き込み後、次の順で確認してください。

```text
make app off
make app 1:255,128,0
make app 2:255,128,0
make app 3:255,128,0
make app 4:255,128,0
make app 5:0,255,128
make app 6:0,255,128
make app 7:0,255,128
make app 8:0,255,128
make app on
make app off
```

成功条件は、個別指定で指定した1灯だけが点灯し、`on`で8灯、`off`で全消灯することです。
