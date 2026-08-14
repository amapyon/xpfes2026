# 赤外線受信・16進表示 PoC

PART-08（VS1838B）で38kHz赤外線信号を受信し、UIAPduino Pro Micro
CH32V003 V1.4でデコードしてPCへ送る主催者向けPoCです。PCには受信データを
16進数で表示します。

## 完了状況

2026-08-13にWindows実機で、次の項目を確認しました。

- NEC、NEC extended、NEC repeatのデコード
- 東芝エアコン72bit状態フレームのデコードとXORチェックサム検証
- 東芝エアコンとNECを同一セッション内で自動判別
- Vendor-defined USB HIDによるPCへの送信
- PCでの16進数表示
- 混在受信時も`errors=0`

実機で確認したコード:

```text
0xF20D03FC0190010090  TOSHIBA_AC  72bit checksum=OK
0xF20D03FC0190070096  TOSHIBA_AC  72bit checksum=OK
0x17E842BD  NEC  address=0x17  command=0x42
0x17E842BD  NEC-repeat (repeat)  address=0x17  command=0x42
```

東芝リモコンは同一状態フレームを2回送信するため、同じ16進数が2行表示されます。
これは受信エラーではありません。

## 対応プロトコル

| プロトコル | 対応内容 |
|---|---|
| NEC | 8bitアドレス、コマンド、各反転値を検証 |
| NEC extended | 16bitアドレス、コマンド反転値を検証 |
| NEC repeat | 直前のNECコードをrepeatとして表示 |
| TOSHIBA_AC | 56/72/80bit、長さ・反転バイト対・XORチェックサムを検証 |

RC-5、RC-6、SONY SIRCなどは未対応です。

## 構成

```text
赤外線リモコン
      ↓ 38kHz
PART-08（復調、アクティブLow）
      ↓ D12 / A3 / PD2 / TIM1_CH1
UIAPduino（タイミング計測・プロトコル判定・デコード）
      ↓ Vendor-defined USB HID
PCアプリ（再結合・16進数表示）
```

信号幅はTIM1入力キャプチャを1MHzで動作させて測定します。USBが使用する
`PD3 / PD4 / PD5`と赤外線入力`PD2`は競合しません。

## 配線

詳細と初回の安全確認は[WIRING.md](WIRING.md)を参照してください。

| PART-08 | UIAPduino | 備考 |
|---|---|---|
| VCC | 5V | センサー電源 |
| GND | GND | 共通GND |
| OUT | D12 / A3 | 100Ω直列、MCUはPD2 / TIM1_CH1 |

旧版の`D5 / PC3`ではなく、必ず`D12 / A3`を使用してください。

## ビルドと実行

UIAP Devkitの起動ファイルから開いたターミナルで、このディレクトリへ移動します。

```bat
cd C:\pj\xpfes2026\workspace\poc\ir_recv_poc
make doctor
make
make size
```

UIAPduinoをUSBブートローダーモードにして書き込みます。

```bat
make flash
```

通常モードで再接続してPCアプリを起動します。

```bat
make app
```

終了は`Ctrl+C`です。接続機器の確認だけを行う場合は`make list`、USB機器なしで
PC側処理を確認する場合は次を使います。

```bat
make doctor
"C:/uiap/uiap-devkit-win64/runtime/win/python/python.exe" host/ir_recv_host.py --self-test
```

## 表示内容

通常時は約1秒ごとに診断状態を表示します。

```text
状態: OUT=HIGH（待機） edges=964 state=0 bits_max=72 errors=0  last=622/2205us max=9099/4487us  reject=0/state0/0us
```

| 項目 | 意味 |
|---|---|
| `OUT` | PART-08出力。通常はHIGH、受信パルス中はLOW |
| `edges` | 起動後に検出した立ち上がり・立ち下がりの累計 |
| `state` | 内部デコーダー状態。待機時は0 |
| `bits_max` | 起動後、1フレームで到達した最大bit数 |
| `errors` | タイミング、形式、チェックサムなどで破棄した回数 |
| `last` | 最後に測定したmark/space時間（µs） |
| `max` | 最大mark/space時間（µs） |
| `reject` | 最後の破棄理由、状態、測定時間。正常時は0 |

`edges`と`bits_max`は累積値なので、PCアプリを再起動してもUIAPduinoをリセットするまで
0には戻りません。

## USB HIDレポート

USB IDは`1209:D009`、Product文字列は`UIAP IR Receiver PoC`、入力レポート長は
8byteです。

### NECイベント

| byte | 内容 |
|---:|---|
| 0 | イベント連番 |
| 1 | `1`=NEC、`2`=NEC extended、`3`=NEC repeat |
| 2..5 | 赤外線で受信した4byte（到着順） |
| 6 | bit0=アドレス反転一致、bit1=コマンド反転一致 |
| 7 | bit数（32） |

### 東芝エアコンイベント

東芝状態は最大10byteあるため、4byteずつ最大3レポートに分割し、PC側で再結合します。

| byte | 内容 |
|---:|---|
| 0 | イベント連番 |
| 1 | `0x20`（TOSHIBA_AC） |
| 2 | 分割番号（0～2） |
| 3 | 全データ長（7、9、10byte） |
| 4..7 | 状態データ4byte。最終レポートの余りはゼロ |

東芝形式は約4.4ms/4.3msのリーダー、約580µsのbit mark、約490/1600µsの
spaceを使用し、各byteをMSB-firstで復元します。先頭4byteの反転関係、byte 2の
長さ、末尾XORチェックサムが一致したときだけ送信します。

### 診断レポート

有効イベントがない間は、`0x10`～`0x13`の診断レポートを間引いて送信します。
入力レベル、エッジ数、最終・最大タイミング、破棄理由をPC側の状態行に反映します。

## トラブルシューティング

- `edges=0`のまま: OUT配線、端子印字、GND共有、`D12 / A3`への接続を確認する。
- `edges`だけ増える: 未対応プロトコル、またはタイミング条件外の可能性がある。
- `bits_max`が途中で止まり`errors`が増える: `reject`の値とログ全体を保存して確認する。
- `OUT=LOW`が続く: OUT/VCC/GNDの取り違え、受光部への連続光、配線不良を確認する。
- 同じ東芝コードが2回表示される: リモコンが同一フレームを2回送信しており正常。
- `make app`で接続できない: 通常モードへの切り替えと`make list`の結果を確認する。

仕様が不明なリモコンは、状態行と受信前後のログを使って実機に合わせて調整します。

## ファイル

| ファイル | 内容 |
|---|---|
| `WIRING.md` | 安全確認を含む配線図 |
| `ir_recv_poc.c` | CH32V003ファームウェア |
| `usb_config.h` | Vendor-defined USB HID設定 |
| `host/ir_recv_host.py` | PC側の受信・再結合・16進表示 |
| `Makefile` | ビルド、書き込み、PCアプリ起動 |
| `POC_STATUS.txt` | 実機検証結果の機械可読サマリー |

## 参考仕様

- [IRremoteESP8266 Toshiba A/C implementation](https://github.com/crankyoldgit/IRremoteESP8266/blob/master/src/ir_Toshiba.cpp)
- [IRremoteESP8266 Toshiba A/C protocol definition](https://github.com/crankyoldgit/IRremoteESP8266/blob/master/src/ir_Toshiba.h)
