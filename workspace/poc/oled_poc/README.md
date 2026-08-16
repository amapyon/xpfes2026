# OLED PoC

PART-09（SSD1306、128×64、I2C）をUIAPduino Pro Micro CH32V003 V1.4へ
接続し、PCのUSB HIDコマンドで文字と図形を描画する主催者向けPoCです。

## 検証結果

Windows実機でPoCが期待どおり動作することを確認済みです。USB HID通信、
I2Cアドレス`0x3C`の検出、SSD1306初期化、バッファ出力、文字、直線、矩形、円、
輪郭表示、内部塗りつぶし、クリア、全面塗りつぶし、デモを確認しました。

最初に試したOLEDの最右列には個体不良による画素欠けがありましたが、別個体では
同じ配線とファームウェアで最右列を含め正常表示しました。

## 実装内容

- 128×64、1bitの1024バイトRAMフレームバッファ
- 5×7ピクセルのASCII `0x20`～`0x7E`
- 1ピクセルの文字間隔（文字セルは6×8ピクセル）
- 範囲外の文字コードは5×7の塗りつぶし
- 出力、クリア、全面塗りつぶし、文字列、直線、矩形、円、デモ
- 矩形と円は輪郭表示／内部塗りつぶしを選択可能
- I2Cアドレス`0x3C`/`0x3D`の接続診断
- PC1/PC2を使うソフトウェアI2Cとrv003usbの共存
- Windows実機実績のある25バイトFeature Report（長い文字列は自動分割）

文字列の位置は文字セルで指定します。列は0～20、行は0～7です。図形は
左上原点のピクセル座標で指定します。

## 初回確認

電源・端子条件が未確認のため、最初に[WIRING.md](WIRING.md)を読み、実物確認を
完了してください。確認前の実機接続や書き込みは行いません。

## ビルド

Devkitの`start-uiap.cmd`（Windows）または`start-uiap.command`（macOS）から
環境を開き、このディレクトリへ移動します。

```text
make self-test
make
make size
make flash
```

## 操作例

描画コマンドはRAMバッファだけを変更し、`output`でまとめてOLEDへ反映します。

```text
make probe
make clear
make text COL=1 ROW=1 TEXT="Hello"
make line X0=0 Y0=20 X1=127 Y1=20
make rect X0=4 Y0=24 X1=50 Y1=60
make circle X=92 Y=42 R=17
make output
make status
```

矩形または円を塗りつぶす場合は`FILL=1`を追加します。省略時は輪郭のみです。

```text
make rect X0=4 Y0=24 X1=50 Y1=60 FILL=1
make circle X=92 Y=42 R=17 FILL=1
make output
```

デモだけは作成したバッファを自動的に出力します。

```text
make demo
```

任意の1バイトはPCプログラムを直接呼び出して`\xNN`で指定できます。例えば
`0x1F`と`0x7F`が5×7塗りつぶしになることを確認するには次を実行します。

```text
python host/oled_host.py clear
python host/oled_host.py text 0 0 "A\x1f\x7fZ"
python host/oled_host.py output
```

## 仕様上の判断

- 文字セルは6×8ピクセル。文字本体5×7、右1列と次行との1行を空きとする。
- 21列目（列20）は画面右端に収まる文字だけ表示し、続く文字はクリップする。
- 線と円は画面外にはみ出した部分をクリップする。
- 矩形は左上座標が右下座標以下でなければエラーにする。
- OLEDへの転送中もUSB割り込みを許可する。I2Cクロックが伸びる可能性はあるが、
  ソフトウェアI2Cは各ビットを状態遷移で生成するためデータ順は維持される。

USBのバイト配置は[PROTOCOL.md](PROTOCOL.md)に記載しています。

## ファイル

| ファイル | 内容 |
|---|---|
| `oled_poc.c` | ファームウェア、SSD1306、描画処理 |
| `usb_config.h` | Vendor-defined HID記述子 |
| `host/oled_host.py` | PC側コマンド |
| `WIRING.md` | 段階確認式の配線図 |
| `PROTOCOL.md` | USBプロトコル |
| `POC_STATUS.txt` | 検証状況 |

## 実機確認で記録する値

- OLED基板表裏の写真と端子を見る向き
- 対応VDD、実測VDD
- SDA-VDD、SCL-VDD間の抵抗
- 無信号時のSDA/SCL電圧
- 検出アドレス（0x3Cまたは0x3D）
- `make size`のFlash/RAM使用量
- デモ表示、各コマンド、USB再接続後の動作

## Feature Report送信エラー

初版の64バイトFeature ReportはWindowsでデバイス列挙まで成功したものの、
`HidD_SetFeature`がエラー`0x0000001F`となりました。現在は既存PoCで実績のある
25バイトへ変更し、長い文字列をPC側で19バイトずつ自動分割します。

この変更はUSB HID記述子を変更するため、古いファームウェアのままPC側プログラム
だけを更新しても動作しません。`make flash`後にUSBを一度抜き、通常モードで
挿し直してから`make probe`を実行してください。

実機再試験では25バイト版の送信に成功し、PART-09をI2Cアドレス`0x3C`で検出、
SSD1306の初期化まで成功しました。表示内容と表示方向は`make demo`で確認します。

最初に試験したOLED個体では、最端列`x=127`だけに画素欠けが確認されました。
内側の列は連続表示され、別のPART-09個体では`x=127`を含む全周が正常表示された
ため、描画処理や表示RAM転送ではなく最初のOLED個体の不良と判断します。

標準デモの外枠は表示領域全体の確認も兼ね、`(0,0)`～`(127,63)`のままです。
これにより四辺の端画素を目視検査できます。
