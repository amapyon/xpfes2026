# 東芝エアコン赤外線送信 PoC

PCからVendor-defined USB HIDで指示し、UIAPduino Pro Micro CH32V003 V1.4と
赤外線LED `OSI5FU3A11C`から38kHz赤外線を送信する主催者向けPoCです。東芝エアコンのON/OFFを
成功条件とします。

## 現在の状態

- ファームウェア、PCアプリ、配線図を作成済み
- PC側のフレーム検証テストを実行可能
- ファームウェアのビルドとPC側自己テストは確認済み
- 書き込み・実機送信は未確認
- 赤外線LEDはOptoSupply `OSI5FU3A11C`（3mm、940nm、連続最大100mA）を採用
- LED直列抵抗は`82Ω（1/2W以上）`とし、約45～48mAで駆動
- MOSFETは`MTB30N06I3`を採用（5Vゲート駆動、G-D-S端子順を反映済み）
- LEDの極性と対象エアコンでのON/OFFは要確認

## 使用するコード

受信PoCで2026-08-13に実機取得した72bitコードを初期値にしています。

| 操作 | 送信データ |
|---|---|
| ON | `F2 0D 03 FC 01 90 01 00 90` |
| OFF | `F2 0D 03 FC 01 90 07 00 96` |

東芝の状態送信方式では、単純な共通ON/OFFコマンドではなく、運転モードなどを含む
状態フレームを送ります。この2コードは受信PoCで取得した個体向け初期値です。

## 構成

```text
PCアプリ
  ↓ Vendor-defined USB HID Feature Report
UIAPduino（フレーム検証・TIM1_CH4で38kHz PWM生成）
  ↓ D6/A2 / PC4 → MOSFET駆動回路
OSI5FU3A11C 赤外線LED
  ↓ 東芝72bit状態フレームを2回送信
東芝エアコン
```

送信タイミングは、受信PoCとIRremoteESP8266の東芝実装に合わせ、リーダー
`4400/4300µs`、bit mark `580µs`、0/1 space `490/1600µs`、38kHz、50% Duty、
MSB-firstです。
送信バースト中はUSB割り込みを一時停止し、ソフトウェアで作るmark/space時間が
USB通信によって伸びないようにしています。Feature Reportのコマンドは専用バッファへ
退避し、USB制御転送の完了応答を返してから送信を開始します。送信完了後は直ちに
USB処理を再開します。Windowsでは送信中の状態取得が一時的に`read error`になる場合が
あるため、PCアプリは最大2秒間再試行します。

## ビルド前の確認

まず[WIRING.md](WIRING.md)を読み、部品の型番・極性を確認してください。配線安全確認が
`未確認`の間は、回路を接続した通電や書き込みを行いません。

UIAP Devkitの起動ファイルから開いたターミナルで実行します。

```bat
cd C:\pj\xpfes2026\workspace\poc\ir_send_poc
make doctor
make
make size
```

PC側のコード処理だけなら、基板なしで確認できます。

```bat
make self-test
```

安全確認後、UIAPduinoをUSBブートローダーモードにして書き込みます。

```bat
make flash
```

通常モードで再接続し、赤外線LEDをエアコンの受光部へ向けて操作します。

```bat
make on
make off
make status
```

受光感度の切り分けでは、瞬時LED電流を変えずに送信回数だけ4回へ増やせます。

```bat
make on COUNT=4
```

検証回路は、LEDごとに直列抵抗`82Ω（1/2W以上）`を使用します。データシートの
代表VF 1.35Vから、5.00～5.25V時の瞬時電流は約44.5～47.6mAです。これは放射強度の
測定条件50mAに近く、連続最大100mAにも余裕があります。

旧PART-07による試験では、送信コードと復調タイミングは純正リモコンと一致した一方、
到達距離が不足しました。新しいLEDは半値角15°のため、まずエアコン受光部から10～30cm、
ほぼ正面でON/OFFを確認します。2灯を使う場合は並列2枝とし、各LEDに個別の82Ω抵抗を
接続します。詳細は[WIRING.md](WIRING.md)を参照してください。

データシートのパルス順方向電流1Aは、パルス幅100µs以下かつDuty 1/100以下の条件です。
現在の38kHz・約50% Dutyには適用できません。

## 別コードを試す

対象機種が反応しない場合は、`ir_recv_poc`で対象リモコンのONとOFFを受信し、表示された
16進数をそのまま`raw`へ渡します。長さ・反転byte・XORチェックサムはPCとデバイスの
両方で検証します。

```bat
make raw CODE=F20D03FC0190010090
```

または直接実行して、送信回数を1～4で指定できます。

```bat
"%UIAP_PYTHON%" host\ir_send_host.py raw F20D03FC0190010090 --count 2
```

## USBレポート

USB IDは共有テスト用`1209:0001`、Productは`UIAP IR Sender PoC`、Feature Reportは14byteです。

`1209:0001`は世界で一意ではなく、教育目的の試作とワークショップ内テスト専用です。製品、製造、販売、再配布には使用できません。

| byte | SET時 | GET時 |
|---:|---|---|
| 0 | Report ID `1` | Report ID `1` |
| 1 | command `1`=東芝送信 | status `0`=idle、`1`=sent、`2`=bad command、`3`=bad frame |
| 2 | データ長（7/9/10） | 最後に成功したデータ長 |
| 3 | 送信回数（1～4） | 最後に成功した送信回数 |
| 4..13 | 赤外線データ。余りは0 | 0 |

## 実機で確認する順序

1. `make self-test`がPASSする。
2. ファームウェアがビルドできる。
3. 配線安全確認を完了する。
4. カメラまたはPART-08で、送信時だけ38kHzバーストが出ることを確認する。
5. `make on`でエアコンがON、`make off`でOFFになることを確認する。
6. 反応しない場合は、距離・向き、受信PoCでの再受信結果、対象エアコンとリモコンの
   型番を記録して調整する。

### 発光するがエアコンが反応しない場合

光って見えることだけでは、38kHz、mark/space時間、送信コード、光量が正しいとは
判断できません。次の順序で切り分けます。

1. このディレクトリの最新版を再ビルド・再書き込みする。
2. PART-08受信PoCを送信LEDから5～10cmに置き、`make on`を受信する。
3. 受信表示が`0xF20D03FC0190010090 TOSHIBA_AC 72bit checksum=OK`になるか確認する。
4. 正しく受信できたら、エアコン受光部から5～10cm、正面に近い位置で試す。
5. PART-08で別コードになる、`errors`が増える、または受信できない場合は、受信PoCの
   状態行とログを保存する。抵抗値はまだ変更しない。

### 送信機と受信機を2台同時に使う場合

通常モードでは、送信機と受信機は同じ共有テスト用VID:PID `1209:0001`を使用し、Product文字列`UIAP IR Sender PoC`と
`UIAP IR Receiver PoC`で区別します。各ディレクトリで
`make list`を実行し、それぞれ1台と表示されることを確認してからアプリを起動します。

送信機が0台の場合は、いったん受信機を外し、送信機だけを接続して`make list`を試します。
それでも0台なら、送信機をUSBブートローダーモードにして送信ファームウェアを再書き込みし、
通常モードで挿し直します。2台を接続したまま`make flash`を実行すると書き込み対象を
取り違える可能性があるため、書き込み時は対象基板だけを接続します。

## ファイル

| ファイル | 内容 |
|---|---|
| `WIRING.md` | 配線図、安全確認、段階試験 |
| `ir_send_poc.c` | CH32V003ファームウェア |
| `usb_config.h` | Vendor-defined USB HID設定 |
| `host/ir_send_host.py` | PC側ON/OFF/raw/statusアプリ |
| `Makefile` | ビルド、書き込み、操作 |
| `POC_STATUS.txt` | 現在の検証状態 |

## 参考

- 受信・実測コード: `workspace/poc/ir_recv_poc`
- [IRremoteESP8266 Toshiba A/C implementation](https://github.com/crankyoldgit/IRremoteESP8266/blob/master/src/ir_Toshiba.cpp)
- [IRremoteESP8266 Toshiba A/C protocol definition](https://github.com/crankyoldgit/IRremoteESP8266/blob/master/src/ir_Toshiba.h)
- [CYStech MTB30N06I3データシート](https://akizukidenshi.com/goodsaffix/MTB30N06I3.pdf)
- [秋月電子 MTB30N06I3製品情報](https://akizukidenshi.com/catalog/g/g115850/)
- [秋月電子 OSI5FU3A11C製品情報（商品番号104313）](https://akizukidenshi.com/catalog/g/g104313/)
- [OptoSupply OSI5FU3A11Cデータシート](https://akizukidenshi.com/goodsaffix/OSI5FU3A11C.pdf)

購入情報は2026-08-14確認時点で、10個入り200円（税込）、在庫ありです。価格と在庫は
購入時に商品ページで再確認してください。
