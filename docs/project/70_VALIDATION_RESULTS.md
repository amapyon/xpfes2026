# 検証結果

更新日: 2026-08-05

## 1. この文書の目的

この文書は、XP祭り2026向けUIAP Devkit、UIAPduino Pro Micro CH32V003 V1.4、USB HID、外付け部品、PC側アプリケーションについて、実際に確認した範囲を記録する。

次を区別する。

- 実装済み
- ビルド確認済み
- 書き込み確認済み
- USB列挙確認済み
- HID送受信確認済み
- PC側処理確認済み
- 物理動作確認済み
- 再起動後の再現確認済み
- オフライン確認済み
- Windows確認済み
- macOS確認済み
- 参加者向け採用済み

一段階の成功を、後続段階の成功として扱わない。

この文書の記録は、ワークショップの最終制作物または必須演習としての採用決定を意味しない。採用状態は`90_DECISIONS.md`を参照する。


## 1.1 2026-08-01以降のリリース方針変更

過去の検証記録にある「最終オフラインZIP」「ネットワーク切断状態」「macOS 15最低対応環境」は、その時点の判定条件を示す履歴として残す。2026-08-01以降の現行リリース方針は次とする。

- 最終参加者向けDevkitもオンライン・ブートストラップ方式
- Windows版はMSYS2を使用しないxPackネイティブ構成
- macOSはApple SiliconのmacOS 26以降のみを正式対象
- macOS版にもPythonとhidapiを含める
- Windowsの未文書化カーソルAPIとmacOSの非公開CoreGraphics APIは、リスク明記とリリースごとの回帰検証を条件に採用を許容
- Devkitバージョンは`MAJOR.MINOR.PATCH`の3桁のみを使用

この変更により、過去に「オフライン未確認」「macOS 15未確認」と記録した項目は、今後のリリース阻害条件ではない。ただし過去の実機事実そのものは変更しない。

## 2. 共通検証環境

### 対象ボード

```text
UIAPduino Pro Micro CH32V003 V1.4
MCU: CH32V003
USBブートローダー: 1209:B803
```

### WindowsネイティブPoCで使用した主な依存関係

| コンポーネント | 検証時の値 |
|---|---|
| xPack Windows Build Tools | 4.4.1-3 |
| xPack GNU RISC-V Embedded GCC | 14.2.0-3 |
| ch32fun | `1e4887e11d4bfa739ed5604524b69f5be9f9275b` |
| rv003usb | `75d926abe89a3002020b989015eab97ce5ad0470` |
| minichlink | `38e653f8354ea8fc19da5f2595cf9958d26738e7` |
| Python | 3.14.6 embeddable x64 |
| hidapi | 0.15.0、CPython 3.14、Windows x64 |

### OS

- Windows 11 x64: 実機確認済み
- macOS Apple Silicon: macOS 26.5.2、Devkit起動、オンラインsetup、arm64版minichlink生成、必須演習3本を利用者実機確認済み。ロータリーカーソル演習はCW／CCW、サイズ変更、`Ctrl+C`終了時復元まで確認
- Windows 11 ARM64: サポート対象外
- Intel Mac: サポート対象外

Windowsの詳細ビルド番号、CPU型番、別ユーザー権限は今回の記録では未取得である。

### 配布方式

今回のWindows PoCはオンライン・ブートストラップ型で検証した。

最終参加者向けオフライン配布版としては未確認である。

## 3. 検証結果一覧

| ID | 日付 | 検証内容 | Windows | macOS | 状態 |
|---|---|---|---|---|---|
| WIN-ENV-001 | 2026-07-24 | Devkit起動、セットアップ、再起動後再現 | 合格 | 未確認 | PoC合格 |
| WIN-DOWNLOAD-TEST15-001 | 2026-08-01 | test15オンラインsetupの進捗表示と主要4取得物 | 利用者報告で合格 | 対象外 | Build Tools、GCC、Python、hidapiの取得・SHA-256・配置合格 |
| WIN-CH32FUN-HASH-TEST15-001 | 2026-08-01 | test15 ch32fun入力アーカイブSHA-256 | 利用者報告で不合格 | 対象外 | ZIP取得にtar.gzの期待値を使用 |
| WIN-CH32FUN-TEST16-STATIC-001 | 2026-08-01 | test16ロック修正と隔離ファイル再検証 | 静的検査合格 | 対象外 | Windows実機setup完走は未確認 |
| WIN-PATH-001 | 2026-07-26 | 空白・全角文字を含む展開先で`UIAP-E103`表示 | 利用者報告 | 対象外 | 非対応パスでの停止表示を確認 |
| WIN-PATH-002 | 2026-07-26 | 有効な複数階層ASCIIパスをtest11が誤って拒否 | 利用者報告 | 対象外 | 回帰不具合・原因特定・修正版未検証 |
| DOC-NAV-001 | 2026-07-29 | 演習移動用トップレベルコマンド廃止と明示的`cd`方針 | 文書更新 | Lチカで合格 | 全演習のDevkit実装・実機検証待ち |
| MAC-GATEKEEPER-001 | 2026-07-27 | 未署名・未公証ZIPの初回起動と個別許可 | 対象外 | 利用者確認 | Gatekeeper個別許可が必要 |
| MAC-PATH-001 | 2026-07-27 | `start-uiap.command`のDevkitルート解決 | 対象外 | 合格 | `0.1.2-test3`で修正確認 |
| MAC-ENV-001 | 2026-07-27 | arm64ネイティブ起動、Rosetta不使用、環境変数と初期ディレクトリ | 対象外 | 合格 | `0.1.2-test3`以降でPoC合格 |
| MAC-SETUP-001 | 2026-07-27 | xPack GCC、ch32fun、rv003usbのオンラインsetup | 対象外 | 合格 | SHA-256確認を含む |
| MAC-MAKE-001 | 2026-07-27 | Devkit内GNU Make 4.4.1 arm64 | 対象外 | 合格 | `0.1.3-test4`でPoC合格 |
| MAC-LED-BUILD-001 | 2026-07-27 | `00_onboard_led_blink`のビルドと生成物 | 対象外 | 合格 | FLASH 444 B、RAM 0 B |
| MAC-MINICHLINK-BUILD-001 | 2026-07-29 | libusb静的ビルドとarm64版`minichlink`生成 | 対象外 | 合格 | test8主催者PoC合格 |
| MAC-MINICHLINK-QUARANTINE-001 | 2026-07-29 | `minichlink`単体の隔離属性処理と署名検証 | 対象外 | 合格 | test7不具合をtest8で修正 |
| MAC-FLASH-001 | 2026-07-29 | `1209:B803`検出、CH32V003書き込み、ブート | 対象外 | 合格 | test8主催者PoC合格 |
| MAC-LED-PHYSICAL-001 | 2026-07-29 | 基板上LEDの0.2秒点灯・0.8秒消灯 | 対象外 | 合格 | 物理動作確認済み |
| MAC-DOCTOR-TEST9-001 | 2026-07-31 | test9主催者診断、ネイティブホストを含む | 対象外 | 合格 | `PASS=53 WARN=3 FAIL=0`。実機機能確認とは別 |
| MAC-NEWLIB-TEST9-001 | 2026-07-31 | `doctor`のNewlib検査と実コンパイル行の整合性 | 対象外 | 不合格 | `doctor`はPASS、実際は`-I/usr/include/newlib`が残存 |
| MAC-HID-KBD-TEST9-001 | 2026-07-31 | test9マクロキーボードのUSB Device列挙とIOHID列挙 | Windows入力合格 | 不合格 | USB列挙成功、`bDeviceClass=3`、`hidutil`不在、macOS入力不可 |
| MAC-HID-KBD-TEST10-001 | 2026-07-31 | test10マクロキーボードのmacOS入力 | 未確認 | 合格 | 初回アシスタント終了後`AbCdE`、長押し抑止、再押下、キー解放、再接続合格 |
| MAC-NEWLIB-TEST10A-001 | 2026-07-31 | test10a Newlib診断の誤検出修正 | 対象外 | 合格 | 未使用既定値ではなく実効`-I$(NEWLIB)`と必須演習dry-runを検査 |
| MAC-HID-ENC-TEST11-001 | 2026-07-31 | test11ロータリーHIDのUSB・IOHID列挙とCW／CCW | 対象外 | 合格 | `1209:C004`を1台検出し、両方向のHID入力を確認 |
| MAC-CURSOR-TEST11-001 | 2026-07-31 | test11非公開カーソルAPI | 対象外 | 不合格 | 現在値`0.00`、`E207`、`E205`。スカラーABI不一致 |
| MAC-CURSOR-TEST12-001 | 2026-07-31 | test12ロータリーカーソル統合動作 | 対象外 | 合格 | 利用者報告によりCW／CCW、サイズ変更、`Ctrl+C`終了時復元を確認 |
| WIN-LED-001 | 2026-07-24 | 基板上LED点滅 | 合格 | 未確認 | PoC合格 |
| WIN-HID-KBD-001 | 2026-07-24 | D5スイッチによる`AbCdE`入力 | 合格 | 未確認 | PoC合格 |
| WIN-HID-ENC-001 | 2026-07-24 | D8/D9エンコーダーHID入力 | 合格 | 未確認 | PoC合格 |
| WIN-HOST-CURSOR-001 | 2026-07-24 | Pythonホストアプリによるポインターサイズ変更 | 合格 | 未確認 | PoC合格 |
| WIN-HID-MOTOR-001 | 2026-07-19 | HID Feature Reportによる振動モーター制御 | 合格 | 未確認 | 既存PoC合格 |
| WIN-HID-MOTOR-002 | 2026-08-01 | 構成変更後の振動モーターHID PoC再検証 | 利用者報告 | 未確認 | ビルド、書き込み、USB HID制御、物理動作をWindows実機で確認 |
| MAC-HID-MOTOR-001 | 2026-08-02 | 構成変更後の振動モーターHID PoC実機検証 | 合格済み | 利用者報告 | ビルド、書き込み、USB HID制御、物理動作をApple Silicon実機で確認 |
| REL-CH32FUN-SUBSET-001 | 2026-07-25 | ch32fun許可リストサブセット生成・全演習検証 | 未確認 | 未確認 | 方針決定・未実装 |
| USER-BEEP-DIRECT-001 | 2026-07-25 | 5V・50%・2秒のGPIO直結パッシブブザー発音 | 利用者報告 | 未確認 | PoC物理動作報告・電気測定未実施 |
| WIN-HID-POT-HAPTIC-001 | 2026-07-26 | RV09 ADC、Vendor HID、ポインターサイズ、振動の統合 | 合格 | 対象外 | Windows PoC合格 |
| WIN-ADC-POT-STABLE-001 | 2026-07-26 | v1.0.8 ADC安定化と段階ふらつき抑制 | 合格 | 対象外 | 利用者実機合格 |

## 4. WindowsネイティブDevkit起動・再現性

### 対象Devkit

検証の過程で次のテスト版を使用した。

```text
0.1.0-test2
0.2.1-test4
0.3.1-test6
0.3.2-test7
```

各版は、直前の既知問題を修正する目的で作成した検証版である。最終リリース版ではない。

### 確認した手順

1. ZIPを展開
2. `start-uiap.cmd`を起動
3. `setup`を実行
4. `sample`で演習へ移動
5. `make clean`
6. `make flash`
7. コンソールを閉じる
8. `start-uiap.cmd`から再起動
9. `setup`
10. `sample`
11. `make flash`

この手順は当時のテスト版の履歴である。2026-07-27以降の現行方針では`sample`を廃止し、受講者自身が`cd`で演習ディレクトリへ移動する。過去の成功記録を書き換えず、修正版Devkitでは新しい操作方法を別途検証する。

### 結果

- 起動ファイルからCommand Promptを表示: 成功
- オンラインセットアップ: 成功
- GCC、Make、依存関係の取得と展開: 成功
- コンソール再起動後のPATHと環境変数再設定: 成功
- `setup`の再実行: 成功
- 以前のコンソールに残った環境変数へ依存しないこと: 確認

### 未確認

- ネットワーク切断状態
- 別のWindows 11 PC
- 管理者権限のない別ユーザー
- 空白を含む展開先
- Windows Defenderの異なる設定
- 長時間運用

## 5. 基板上LED点滅

### 検証ID

```text
WIN-LED-001
```

### 演習

```text
workspace/exercises/00_onboard_led_blink
```

### 実行コマンド

```text
make clean
make
make flash
```

### ビルド結果

```text
FLASH: 436 B / 16 KB
RAM:   0 B / 2 KB
```

### 書き込み

- ブートローダー`1209:B803`を検出
- CH32V003を検出
- ファームウェア書き込み成功
- 書き込み後にブート成功

### 物理動作

```text
0.2秒点灯
0.8秒消灯
```

基板上LEDが期待周期で点滅することを確認した。

### 再現性

- `make clean`後の再ビルド: 成功
- 再書き込み: 成功
- コンソール再起動後の再実行: 成功

### 発生した問題

Windows形式パスをPOSIX互換`sh`へ渡したため、次のように区切りが消えた。

```text
C:pj...generated__.ld
```

### 修正

Makefile内部で`C:\...`を`C:/...`へ正規化した。

修正後、`generated__.ld`生成、ビルド、書き込み、実機動作が成功した。

## 6. HIDマクロキーボード

### 検証ID

```text
WIN-HID-KBD-001
```

### 対象Devkit

```text
0.2.1-test4
```

### 演習

```text
workspace/exercises/01_macro_keyboard
```

### 配線

| UIAPduino | 部品 | 設定 |
|---|---|---|
| D5 / PC3 | モメンタリスイッチ | 内部プルアップ |
| GND | モメンタリスイッチ | 押下時Low |

### 動作

スイッチを1回押すと、HIDキーボードとして次を入力する。

```text
AbCdE
```

押し続けでは繰り返さず、一度離して再度押すと再送する構成を確認した。

### ビルド結果

```text
FLASH: 2564 B / 16 KB
RAM:   108 B / 2 KB
```

### USB

```text
ブートローダー: 1209:B803
アプリケーション: 1209:C003
USBシリアル番号: TEST3-001
```

`1209:C003`と`TEST3-001`はPoC用一時値である。

Windows上で次の列挙を確認した。

```text
USB 入力デバイス
HID キーボード デバイス
```

### 確認結果

- ファームウェアビルド: 成功
- USBブートローダー書き込み: 成功
- アプリケーション再列挙: 成功
- HIDキーボード認識: 成功
- モメンタリスイッチ入力: 成功
- `AbCdE`入力: 成功

### 発生した問題

1台の物理UIAPduinoについて、親USBデバイスとHID子デバイスを複数ブートローダーとして数える可能性があった。

```text
[UIAP-F205] Multiple bootloaders were detected.
```

### 修正

`USB\VID_1209&PID_B803\...`形式の現在接続中の物理USB親デバイスだけを数えるよう書き込みスクリプトを修正した。

修正後:

```text
[UIAP] One physical bootloader detected. Starting flash.
```

書き込みとHID動作が成功した。

### 未確認

- macOS
- 別キーボード配列
- 長時間連打
- 複数HIDキーボード接続時
- 正式VID:PIDと正式USBシリアル番号

## 7. ロータリーエンコーダーHID入力とポインターサイズ変更

### 検証ID

```text
WIN-HID-ENC-001
WIN-HOST-CURSOR-001
```

### 対象Devkit

```text
0.3.2-test7
```

### 演習

```text
workspace/exercises/02_rotary_cursor_size
```

### 使用部品

検証プログラム上の識別:

```text
RE12000XH1-V02
24 clicks / 24 pulses
```

3端子型エンコーダーとしてA、C、Bを使用した。

### 配線

| UIAPduino | エンコーダー | 設定 |
|---|---|---|
| D8 / PC6 | A | 内部プルアップ |
| GND | C | 共通端子 |
| D9 / PC7 | B | 内部プルアップ |

D5は既存モメンタリスイッチ用として使用せず、初期化も参照もしない構成とした。

### USB HID

```text
アプリケーションVID:PID: 1209:C004
製品名: UIAP RE12000 Cursor Test
USBシリアル番号: TEST7-001
Usage Page: 0xFF00
Usage: 0x0001
```

`1209:C004`と`TEST7-001`はPoC用一時値である。

### PC側アプリケーション

検証時の配置:

```text
workspace/host/cursor_size_host.py
```

2026-07-25に決定した標準配置:

```text
workspace/exercises/02_rotary_cursor_size/host/<platform>/cursor_size_host.py
```

検証時の実装は旧配置を使用した。標準配置への移設後も、配布環境内のPythonとhidapiを使用する。移設後の`make app`、HID受信、ポインターサイズ変更、設定復元は再検証対象とする。

実行:

```text
make app
```

### 確認したログ

```text
起動時サイズ: 80
CW:   96
CW:  112
CW:  128
CW:  144
CW:  160
CCW: 144
CCW: 128
CCW: 112
CCW:  96
CW:  112
```

1クリックにつき16単位で、CWとCCWの両方向に変化することを確認した。

### 確認結果

- ファームウェアビルド: 成功
- 書き込み: 成功
- Vendor-defined HID列挙: 成功
- hidapiによるデバイスオープン: 成功
- CW検出: 成功
- CCW検出: 成功
- Windowsポインターサイズ変更: 成功
- ログファイル生成: 成功
- D5とのGPIO競合なし: 確認

### 発生した問題

セットアップ中のhidapi診断を`python -c`で実行したため、PowerShellとPython間で引用符が崩れた。

```text
SyntaxError: '(' was never closed
[UIAP-E207] Bundled Python could not import hidapi.
```

### 修正

Pythonワンライナーを廃止し、次のような診断ファイルを実行する構成へ変更した。

```text
scripts/python/hidapi_probe.py
```

修正後、同梱Pythonからhidapiをimportし、ホストアプリを起動できた。

### 未確認

- `Ctrl+C`終了時に起動前サイズへ復元
- 強制終了後の`make restore`
- USB切断時の終了と復元
- 再接続後の再起動
- 高速回転時の取りこぼし
- 長時間連続操作
- 別のWindows 11 PC
- macOS Apple SiliconでのPython・hidapi・HIDホストアプリ・オフライン最終ZIP・別Mac検証
- 正式VID:PID
- MCU固有ID由来USBシリアル番号

## 8. 振動モーターHID制御

### 検証ID

```text
WIN-HID-MOTOR-001
WIN-HID-MOTOR-002
MAC-HID-MOTOR-001
```

### 情報源

`WIN-HID-MOTOR-001`は既存の`90_DECISIONS.md`から転記した検証結果である。`WIN-HID-MOTOR-002`は2026-08-01の構成変更後に行ったビルド再現結果と、利用者によるWindows実機動作報告である。`MAC-HID-MOTOR-001`は2026-08-02の利用者によるmacOS Apple Silicon実機動作報告である。

### 確認済み

- Windows 11 x64
- MSYS2 UCRT64環境
- ファームウェアのビルド
- PC側ユーティリティのビルド
- `1209:B803`ブートローダーによる書き込み
- Vendor-defined USB HID Feature Report
- アプリケーション`1209:D003`としての列挙
- 振動レベル`1`～`100`の受信
- 振動強度の変化
- `status`による設定値取得
- `off`による停止

構成変更後の`WIN-HID-MOTOR-002`では、次を再確認した。

- Devkit同梱`riscv-none-elf-gcc`によるクリーンビルド
- `make flash`による書き込み
- アプリケーションUSB HIDとしての動作
- PC側からの振動モーター制御と物理動作

`MAC-HID-MOTOR-001`では、macOS Apple Silicon実機で次を確認した。

- Devkit環境でのファームウェアビルド
- `make flash`による書き込み
- アプリケーションUSB HIDとしての動作
- PC側からの振動モーター制御と物理動作

配線:

```text
D6/A2 → PC4 → TIM1_CH4
```

`1209:D003`はPoC用一時値である。

### 未確認

- 参加者向け必須演習としての採用
- 正式VID:PID
- 長時間動作とUSB電源ノイズの最終評価

## 9. 既知問題と恒久対応

| 問題 | 原因 | 恒久対応 | 確認版 |
|---|---|---|---|
| `generated__.ld`を作成できない | Windowsパスを`sh`へ未変換 | Makefile内部で`C:/...`へ正規化 | `0.1.0-test2` |
| 物理1台を複数ブートローダーと判定 | 親USBとHID子を別々に数えた | 現在接続中の物理USB親だけを数える | `0.2.1-test4` |
| hidapi診断で`SyntaxError` | `python -c`の引用符崩れ | 診断処理を`.py`ファイルへ分離 | `0.3.1-test6` |
| 空白を含むDevkitルートで`setup`末尾のMake dry-runが失敗 | GNU Makeの`include`が空白をファイル区切りとして解釈 | 起動・setup・doctorでASCII空白なしパスを検査し`UIAP-E103`で停止 | `0.4.2-test10`、空白・全角パスの停止表示を利用者確認 |
| `UIAP-E103`の説明が英語だけで初心者が理解しにくい | エラー本文を英語で実装していた | 原因、現在の場所、推奨移動先、再起動手順を日本語化 | `0.4.3-test11`実装、Windows再検証待ち |
| 有効な`C:\pj\xpfes2026\uiap-devkit-win64`を`UIAP-E103`で拒否 | test11の正規表現がバックスラッシュと複数階層を誤って表現 | 判定を共通スクリプトへ集約し、有効・無効パスの自動テストを追加 | `0.4.3-test11`で利用者確認、同版は配布不可 |

詳細な症状と復旧方法は`60_TROUBLESHOOTING.md`を参照する。

## 10. PoC識別子

2026-07-24までの検証で使用した一時値:

```text
1209:C003
1209:C004
1209:D003
TEST3-001
TEST7-001
```

これらは正式な公開配布用VID:PIDまたはUSBシリアル番号として決定されていない。

正式化前に確認する。

- VID:PIDの利用権
- アプリケーションPID
- MCU固有ID由来USBシリアル番号
- 同一VID:PIDでの複数台接続
- WindowsとmacOS双方での列挙
- ホストアプリの選択規則

## 11. 未確認事項一覧

### 開発環境

- 最終オフラインZIP
- ch32fun許可リストサブセットの生成スクリプト
- ch32funサブセットでの全演習ビルド、書き込み、USB、ホストアプリ
- ch32fun対応ソース、SBOM、再生成性
- 100MB以内の最終構成
- 別のWindows 11 x64 PC
- 管理者権限のない別ユーザー
- ネットワーク切断状態
- Windows Defenderの異なる設定
- macOS Apple SiliconでのPython・hidapi、HID列挙・送受信、ホストアプリ、オフライン最終ZIP、別Mac・別ユーザー

### USBと複数デバイス

- 3台同時接続
- MCU固有ID由来USBシリアル番号
- 書き込み待機中の対象選択
- スリープ復帰
- 長時間抜き差し
- HID経由の自動ブートローダー移行
- minichlink読み戻し検証

### 入力・出力部品

- ADC安定化の複数個体・長時間・異なる配線での再現性
- OLEDとUSB
- WS2812BとUSB
- モーターとUSB電源ノイズの複数個体・長時間評価
- エンコーダー高速回転
- 部品個体差

### ホストアプリ

- `cursor_size_host.py`を各演習の`host`へ移設した後の`make app`再検証
- 旧`workspace/host`参照が残っていないこと
- USB切断時の設定復元
- 強制終了後の設定復元
- ログローテーション
- 複数同一デバイス選択
- macOSでの同等機能

## 12. リリース判定

現時点の判定:

| 項目 | 判定 |
|---|---|
| Windowsオンライン・ブートストラップPoC | 合格 |
| Windows Lチカ | 合格 |
| Windows HIDマクロキーボード | 合格 |
| WindowsロータリーエンコーダーHID | 合格 |
| Windowsポインターサイズ変更ホストアプリ | 基本動作合格 |
| Windows振動モーターHID PoC | 合格 |
| Windowsポテンショメーター＋振動統合PoC v1.0.8 | 主要動作合格 |
| ch32fun許可リストサブセット | 方針決定・未実装 |
| 最終オフライン参加者向けZIP | 未確認 |
| macOS Apple Silicon | 必須演習3本合格。ロータリーカーソル統合動作と振動モーターHID PoCの基本動作を確認 |
| ワークショップ必須演習としての採用 | `00`、`01`、`02`を採用済み |

PoC合格を、そのまま最終リリース合格または参加者向け採用済みとして扱わない。

## 13. ch32fun許可リストサブセット

### 検証ID

```text
REL-CH32FUN-SUBSET-001
```

### 決定済み

- 参加者向け`workspace/deps/ch32fun`は許可リスト方式で生成する
- 固定済み上流コミットから、新しい空ディレクトリへ許可ファイルだけをコピーする
- 他MCU向けexamples、`projects`、`build_scripts`、PlatformIO設定は原則として配布しない
- 完全な上流ソース、許可リスト、生成スクリプト、パッチ、再生成手順を対応ソースとして保持する

### 未実装・未確認

- 許可リストファイル
- 生成スクリプト
- 検査スクリプト
- 必須パスと禁止パスの自動検査
- Windows 11 x64でのサブセット生成後全演習ビルドと書き込み
- macOS Apple Siliconでの同検証
- ネットワーク切断状態
- 入力上流アーカイブSHA-256検証
- 再生成した2ツリーのファイル一覧とハッシュ一致
- `SUBSET.md`、`UPSTREAM_COMMIT`、`ALLOWLIST.txt`の生成
- 対応ソースアーカイブ
- SBOMへの`subset`記録
- ライセンスレビュー

### 合格条件

1. 完全版上流ツリーが存在しないクリーン環境で全採用演習をビルドできる
2. WindowsとmacOSで`make flash`まで成功する
3. USB列挙、HID送受信、ホストアプリ、設定復元が成功する
4. 禁止パスが参加者向けZIPに存在しない
5. 必須パスが欠落していない
6. 完全な固定コミット上流ソースから再生成できる
7. 参加者向けZIP、対応ソース、SBOM、`SHA256SUMS`が整合する

合格するまで、最終オフライン参加者向けZIPのリリース判定は未確認とする。

## 14. GPIO直結パッシブブザーPoC

### 検証ID

```text
USER-BEEP-DIRECT-001
```

### 対象

```text
UIAPduino Pro Micro CH32V003 V1.4
ブザー: 12085P、16Ωパッシブブザー
GPIO: D6/A2、PC4、TIM1_CH4
方式: 追加抵抗、ダイオード、トランジスタなし
```

### 利用者実機報告

次の条件で明確な問題が発生しなかったと報告された。

```text
ブザー電源: 5V
PWM通電デューティ比: 50%
連続発音時間: 2,000ms
目視・体感上の結果: 明確な発熱、USB切断、リセット、故障なし
```

この結果は利用者報告であり、プロジェクト文書生成時に独立した測定または再現試験は行っていない。

### 決定したソフトウェア上限

```c
#define MAX_TONE_DURATION_MS  2000u
#define MAX_TOTAL_TONE_MS     2000u
#define DIRECT_DUTY_DIVISOR   2u
#define DIRECT_COOLDOWN_MS    5000u
```

### 確認済みとして扱う範囲

- 指定個体で5V接続による発音ができたという利用者報告
- 指定個体で2,000ms連続発音できたという利用者報告
- 指定個体で50%デューティ比を使用できたという利用者報告
- 上記値をPoCの上限として決定

### 未確認

- GPIOピーク電流と平均電流
- PC4端子の最高・最低電圧
- 5V接続時の端子定格適合
- 誘導性スパイク
- MCU、レギュレーター、ブザーの温度
- 反復耐久と長期信頼性
- 複数個体での再現性
- 更新版ソースのDevkitビルド、書き込み、USB HID、発音
- macOS Apple Silicon

### 判定

- 物理発音: 利用者実機報告あり
- ソフトウェア上限: 決定済み
- 電気的定格内: 未確認
- 参加者向け採用: 不可、主催者用PoC限定


## 15. RV09ポテンショメーター、Windowsポインターサイズ、振動フィードバック統合PoC

### 検証ID

```text
WIN-HID-POT-HAPTIC-001
WIN-ADC-POT-STABLE-001
```

### 日付と対象

```text
日付: 2026-07-26
演習: workspace/exercises/03_pot_cursor_haptic
リビジョン: v1.0.8
OS: Windows 11 x64
ボード: UIAPduino Pro Micro CH32V003 V1.4
```

### 使用部品と配線

- RV09タイプ B10Kポテンショメーターを+5V-GND間へ接続
- ワイパーを68kΩ/100kΩで分圧し、0.1µFを追加してD1/A0へ入力
- +5Vを同じ68kΩ/100kΩで分圧し、0.1µFを追加してD0/A1へ入力
- ドライバー回路内蔵振動モーターモジュールのINをD6/A2（PC4）へ接続
- モジュールVCC-GNDへ+5V/GND、100µFを追加

### ビルドと書き込み

初版では次のエラーを確認した。

```text
RV003USB requires #define FUNCONF_SYSTICK_USE_HCLK 1
```

`FUNCONF_SYSTICK_USE_HCLK=1`と時間換算修正後、ビルド成功。

```text
FLASH: 3428 B / 16 KB
RAM:    252 B / 2 KB
```

書き込みコマンドで`-w`直後のファイル名が空になる問題を確認し、`$(TARGET).bin`を明示して修正した。最終的にブートローダー`1209:B803`経由で書き込み、アプリケーションHID列挙を確認した。

### USB HID

```text
VID:PID: 1209:D003
Usage Page: 0xFF00
Usage: 0x0001
Product: UIAP Pot Cursor Haptic
Serial: POT-HAPTIC-001
```

これらはPoC用一時値であり、正式な公開配布用識別子ではない。

### ホスト側自己テストと列挙

```text
Host protocol, haptic profile, and cursor mapping self-test: PASS
HID check: PASS
```

Windows Embedded Pythonで演習内モジュールをimportできない問題を確認し、各エントリーポイントが自身の`host`ディレクトリを探索パスへ追加するよう修正した。

### Windowsポインターサイズ

HID入力と分離した`make cursor-test`で、Windowsポインターサイズの即時変更を確認した。v1.0.6では追加のカーソル再読込処理により`WinError 6`が発生したため、v1.0.7で修正した。

通常アプリで次の変更ログを確認した。

```text
value=755, level=12/15, pointer=208
value=735, level=11/15, pointer=192
value=541, level= 9/15, pointer=160
value=326, level= 5/15, pointer=96
```

ポテンショメーター値に応じて15段階でポインターサイズが変化した。

### 振動フィードバック

初期パルスは動作していたが、短く弱いため知覚しにくかった。ホスト側へ0～5の振動プロファイルを追加した。

確認済み既定値:

```text
level=4/5
profile=strong
pattern=80ms + 80ms
gap=40ms
```

レベル4でサイズ変更時の振動を知覚できることを利用者実機で確認した。

### ADC安定化

v1.0.7ではADC値が境界付近で揺れ、ポインターサイズが隣接段階を往復した。v1.0.8で次を追加した。

- チャンネル切替後2回破棄
- 16回測定から最大値と最小値を除外した平均
- 5点中央値
- 低域フィルタ
- 3カウントの報告値デッドバンド
- 12カウントの段階ヒステリシス
- 隣接段階の3サンプル確定待ち
- モーター駆動中と停止後50msのADC更新停止

利用者から「OK」と報告され、ポインターサイズのふらつきが解消したものとして記録する。

### 確認済み

- ファームウェアビルド
- USBブートローダー書き込み
- Vendor-defined HID列挙
- ホスト側自己テスト
- ADC 0～1023値受信
- Windowsポインターサイズ15段階変更
- 振動レベル4の知覚性
- stale restore stateの起動前自動復元
- ADC安定化と段階ふらつき抑制

### 未確認

- macOS相当ホスト処理
- 正式VID:PIDとUSBシリアル番号
- USB切断時の設定復元の反復検証
- 強制終了時の復元の反復検証
- スリープ復帰
- 複数個体、別Windows PC、長時間動作
- 最終オフライン参加者向けZIP

- ワークショップ必須演習としての採用

### 判定

- Windows 11 x64統合PoC: 主要動作合格
- ADC安定化v1.0.8: 利用者実機合格
- 参加者向け採用: 未決定
- macOS対応: 未実装

## 2026-08-01 統合環境のMacファームウェア／Windowsホスト互換確認

### 条件

- デバイスファームウェア: macOS test13の`02_rotary_cursor_size`
- USB識別: VID:PID `1209:C004`
- Product: `UIAP Rotary Cursor macOS Test13`
- Serial: `TEST13-002`
- ホスト: 統合リポジトリのWindows版`cursor_size_host.py`
- コマンド: `make app-dry-run`

### 修正前

エンコーダー静止中にも`CCW delta=-35, -34, -33, ...`を連続受信した。Macファームウェアの2バイトレポート`[delta, sequence]`の2バイト目を、Windowsホストが移動量として誤読していた。

### 修正後

Report IDを使用しないDescriptorに合わせ、Windowsホストが常に先頭バイトを`delta`として読むよう修正した。

利用者実機で次を確認した。

- 静止中は値を表示しない
- エンコーダー操作時だけCW／CCWを表示する
- Mac test13ファームウェアの再書き込みは不要
- ホストプロトコル自己診断は合格

### 判定

- Mac test13ファームウェアとWindows dry-runホストの互換動作: 合格
- Windows `make app`による設定変更と終了時復元: この確認では未実施


## 16. Windows展開先パス互換性

### 検証ID

```text
WIN-PATH-001
WIN-PATH-002
```

### WIN-PATH-001: 非対応パス

利用者実機で、フォルダー名に空白または全角文字を含む場所において`UIAP-E103`が表示されることを確認した。

空白パスでは、GNU Makeの次の処理が影響する。

```make
include $(CH32FUN)/ch32fun.mk
```

`CH32FUN`へ空白を含む絶対パスが入ると、GNU Makeは空白を複数ファイル名の区切りとして扱う。

全角文字はPowerShellで扱えても、GNU Make、xPack `sh.exe`、RISC-V GCCまでの文字コード互換性を保証できない。

現行方針では、空白、非ASCII文字、UNCパスを非対応とする。

### WIN-PATH-002: test11の回帰不具合

利用者実機で、次の有効なパスが`UIAP-E103`で拒否された。

```text
C:\pj\xpfes2026\uiap-devkit-win64
```

このパスは次を満たす。

- ローカルドライブ
- ASCIIのみ
- 空白なし
- UNCではない
- 各フォルダー名は半角英数字とハイフンだけ

原因はDevkit `0.4.3-test11`のパス検査用正規表現である。

問題のある形式:

```powershell
$asciiSafePattern = '^[A-Za-z]:\[A-Za-z0-9_.\-]+$'
```

問題点:

- Windowsのバックスラッシュを正しく表現していない
- 複数階層を許可する繰り返しがない
- 有効な通常パスまで拒否する

### 判定

- `C:\pj\xpfes2026\uiap-devkit-win64`: 有効
- `0.4.3-test11`: Windows版リリース候補として不合格
- 日本語メッセージ方針: 維持
- フォルダー移動による回避: 不適切。推奨先も同じ不具合で拒否される可能性がある

### 必要な修正

- パス判定を`scripts/path-check.ps1`へ集約
- `setup.ps1`と`doctor.ps1`の重複正規表現を削除
- 有効な複数階層ASCIIパスを許可
- 非対応パスだけを`UIAP-E103`で拒否
- 判定の自動テストを追加

正規表現を使用する場合の概念例:

```powershell
$asciiSafePattern = '^[A-Za-z]:\\[A-Za-z0-9._-]+(?:\\[A-Za-z0-9._-]+)*$'
```

### 修正版の再検証項目

- `C:\uiap\uiap-devkit-win64`で`start-uiap.cmd`、`setup`、`doctor`: 未確認
- `C:\pj\uiap-devkit-win64`で同手順: 未確認
- `C:\pj\xpfes2026\uiap-devkit-win64`で同手順: 未確認
- 別ドライブの複数階層ASCIIパス: 未確認
- 空白パスで`UIAP-E103`: test11で表示確認済み、修正版では未確認
- 全角パスで`UIAP-E103`: test11で表示確認済み、修正版では未確認
- UNCパスで`UIAP-E103`: 未確認
- 日本語メッセージ: test11で利用者表示確認済み、修正版では未確認

修正版で全項目を確認するまで、パス検査対策をリリース合格としない。


## 17. 演習ディレクトリへの明示的移動

### 検証ID

```text
DOC-NAV-001
```

### 決定した操作方式

- `start-uiap`起動後の初期位置は`workspace`
- 受講者が`cd`で`workspace/exercises/<exercise-name>`へ移動
- 演習固有操作は演習内のMakefileターゲットを使用
- `sample`、`macro`、`blink`、`cursorapp`、`cursorlist`、`cursorrestore`などのトップレベル別名は配布しない

Windows例:

```text
cd /d "%UIAP_WORKSPACE%\exercises\02_rotary_cursor_size"
make hidcheck
make app
```

### 現在の状態

- 根拠文書の更新: 完了
- `99_FULL_PROJECT_GUIDE.md`の再生成: 完了
- Windows Devkit本体から旧`.cmd`を削除: 未実施
- `welcome.cmd`とREADMEのコマンド一覧更新: 未実施
- 各演習Makefileへ必要な`make list`、`make app-dry-run`、`make restore`を実装: 一部実装済み、全演習未確認
- Windows 11 x64での新操作手順の実機確認: 未確認
- macOS Apple Siliconでの新操作手順の実機確認: `00_onboard_led_blink`で確認済み。他演習は未確認

Devkit `0.4.4-test12`には旧トップレベルコマンドラッパーが残っているため、本決定への適合版とは扱わない。
## 18. macOS Apple Silicon Devkit起動・セットアップ・minichlink生成・Lチカ書き込み

### 検証ID

```text
MAC-GATEKEEPER-001
MAC-PATH-001
MAC-ENV-001
MAC-SETUP-001
MAC-MAKE-001
MAC-MINICHLINK-BUILD-001
MAC-MINICHLINK-QUARANTINE-001
MAC-MINICHLINK-SIGN-001
MAC-BOOTLOADER-001
MAC-FLASH-001
MAC-LED-PHYSICAL-001
```

### 検証環境

```text
OS: macOS 26.5.2
CPU: Apple Silicon arm64
Rosetta: 使用せず
Devkit: uiap-devkit-macarm64 0.1.0-test1 ～ 0.1.7-test8
Distribution: Online Bootstrap Test
```

利用者の実機ログに基づく。別のMac、別ユーザー、ネットワーク切断状態、macOS 15最低対応環境では未確認である。

### バージョン別経過

| Devkit | 結果 | 判定 |
|---|---|---|
| `0.1.0-test1` | 未署名・未公証のためGatekeeperが初回起動を停止 | 個別許可手順が必要 |
| `0.1.1-test2` | Devkitルートを`Downloads`と誤認 | 配布不可 |
| `0.1.2-test3` | ルート解決を修正。ただし`/usr/bin/make`依存 | ビルド基盤未完 |
| `0.1.3-test4` | Devkit内GNU Makeを導入し、Lチカビルドを確認 | ビルド段階合格 |
| `0.1.4-test5` | `minichlink`導入方式の検討版 | 最終方式にしない |
| `0.1.5-test6` | `build-minichlink`初版。GNU Make依存検査に誤検出 | 修正必要 |
| `0.1.6-test7` | 依存検査修正。生成`minichlink`の隔離属性により`Killed: 9` | 隔離属性対策必要 |
| `0.1.7-test8` | 隔離属性除去、アドホック署名、署名検証を自動化し、書き込みとLED点滅を確認 | 主催者PoCの書き込み段階合格 |

### オンラインsetup

取得・確認した主なコンポーネント:

| コンポーネント | 値 | 結果 |
|---|---|---|
| GNU Make | 4.4.1 arm64 | Devkit内部から起動成功 |
| xPack GNU RISC-V Embedded GCC | 14.2.0-3 arm64 | ダウンロード、SHA-256、展開成功 |
| ch32fun | `1e4887e11d4bfa739ed5604524b69f5be9f9275b` | 取得成功 |
| rv003usb | `75d926abe89a3002020b989015eab97ce5ad0470` | 取得成功 |
| libusb | 1.0.29 | arm64静的ライブラリのビルド成功 |
| minichlink | `38e653f8354ea8fc19da5f2595cf9958d26738e7` | Mach-O arm64としてローカル生成成功 |

ツールチェーンアーカイブは約316 MBであった。これはオンライン検証版の実績であり、最終ZIPサイズやオフライン構成の決定ではない。

主催者専用`build-minichlink`はXcode Command Line ToolsのclangとmacOS SDKを使用した。参加者向け最終版でXcode Command Line Toolsを要求してよいことを意味しない。

### 入力と成果物の観測SHA-256

```text
ch32fun source archive: 37a507fa58710a14dbd3e959def57b02a6b0b1d410c9e307653e22aeb081ba9f
libusb 1.0.29 archive: 5977fc950f8d1395ccea9bd48c06b3f808fd3c2c961b44b0c2e6e29fc3a70a85
minichlink binary: 56515fb09d3d3f5d44f747f37bee6aee004e65e3cc4c41ab2dedae0cd738121e
```

当該実行で観測した値であり、最終リリース用固定値と再現ビルド保証は未完了である。

### minichlinkの依存関係と署名

確認済み:

- Mach-O 64-bit executable arm64
- libusbは静的リンク
- 動的依存はmacOSのシステムライブラリとフレームワークのみ
- `/opt/homebrew`、`/usr/local`、開発者ホーム配下のdylib依存なし
- `com.apple.quarantine`なし
- アドホック署名あり
- `codesign --verify`成功
- ビルド来歴ファイルあり

`0.1.6-test7`では、ブラウザから取得したDevkitの隔離属性がローカル生成した`minichlink`へ継承され、`make flash`が`Killed: 9`で終了した。`minichlink`単体から隔離属性を除去すると起動・USB接続・書き込みが成功したため、`0.1.7-test8`で単体処理、署名、検証を自動化した。

### doctor結果

`0.1.7-test8`:

```text
PASS=32 WARN=1 FAIL=1
```

残る項目:

```text
[WARN] ch32fun is a test subset, not the final reviewed allowlist subset.
[FAIL] Bundled Python is not installed.
```

`UIAP-E299`は参加者向けリリース阻害を正しく示している。書き込みツール自体の不合格ではない。

### Lチカビルド・書き込み・物理動作

実行場所:

```text
workspace/exercises/00_onboard_led_blink
```

実行:

```sh
make clean
make flash
```

ビルド結果:

```text
FLASH: 444 B / 16 KB (2.71%)
RAM:     0 B / 2 KB  (0.00%)
```

書き込み成功の主要表示:

```text
VID:0x1209, PID:0xb803
Halting Boot Countdown
Detected CH32V003
Writing image
Image written.
Booting
```

物理動作:

```text
基板上LED: 0.2秒点灯、0.8秒消灯
```

これにより、ビルド確認済み、書き込み確認済み、ブート確認済み、物理動作確認済みとする。LチカファームウェアはUSBアプリケーション列挙を目的としないため、HID列挙確認済みとは扱わない。

### 一時的なブートローダー捕捉失敗

最初の再試行で次を確認した。

```text
VID:0x1209, PID:0xb803
Error: Could not initialize b003boot programmer
```

RESETを押したままUSB接続し、RESETを離して直ちに`make flash`を再実行すると成功した。原因はブートローダー待機状態を捕捉できなかった可能性が高いが、単一実機の結果だけを根拠に断定しない。

### 未確認

- Devkit内Pythonとhidapi
- HID送受信とホストアプリ
- 最終許可リスト版`ch32fun`
- `ch32fun`とlibusb入力SHA-256の正式固定
- `-I/usr/include/newlib`除去後または同パス不在環境での全演習ビルド
- ネットワーク切断状態
- 最終オフラインZIP
- Developer ID署名・公証
- 別のApple Silicon Mac、別ユーザー
- macOS 15最低対応環境
- 参加者向け採用

## 19. macOS HIDマクロキーボード test9・test10実機検証

### 検証環境

```text
OS: macOS 26.5.2
Architecture: Apple Silicon arm64
Rosetta: 使用せず
Board: UIAPduino Pro Micro CH32V003 V1.4
```

### test9: `0.1.8-test9`

`doctor`は次で終了した。

```text
PASS=53 WARN=3 FAIL=0
```

この結果は、ツール、署名、隔離属性、静的検査、ネイティブホスト自己診断が主催者検証用の合格条件を満たしたことを示す。USB HID入力や物理操作の合格を意味しない。

`01_macro_keyboard`の実コンパイル結果:

```text
FLASH: 2332 B / 16 KB
RAM:    216 B / 2 KB
```

最初の`make flash`ではブートローダー待機を捕捉できず失敗した。RESET操作後の再実行で次を確認した。

```text
Detected CH32V003
Writing image
Image written.
Booting
```

macOSでは文字入力できなかった。低レベル確認では次だった。

```text
idVendor:  4617  = 0x1209
idProduct: 49155 = 0xC003
bDeviceClass: 3
USB Product Name: UIAP Macro Keyboard Test
```

- `ioreg`: USB Deviceとして列挙
- `hidutil list`: 対象なし
- macOS入力: 不合格
- 同じ書き込み済みデバイスをWindowsへ接続: `AbCdE`入力合格

この結果から、GPIO、キーシーケンス、Interrupt INの基本動作はWindowsで確認できた一方、macOSのIOHIDバインドに問題があると切り分けた。

また、test9の`doctor`はNewlib依存なしと表示したが、実コンパイル行には次が残っていた。

```text
-I/usr/include/newlib
```

このPASS判定は検査漏れとして不合格に訂正する。

### test10: `0.1.9-test10`

修正内容:

- Device Descriptorの`bDeviceClass`、`bDeviceSubClass`、`bDeviceProtocol`を`0`
- Interface DescriptorでHID Boot Keyboardを宣言
- `GET_REPORT`
- `GET_IDLE`、`SET_IDLE`
- `GET_PROTOCOL`、`SET_PROTOCOL`
- 初期レポートを全キー解放状態
- 未使用LED Output Reportを削除
- Newlibオプション除去と必須演習3本のdry-run検査

初回接続時、macOSのキーボード設定アシスタントが起動し、「左Shiftキーの右隣のキー」を要求した。このデバイスに該当キーはないため、前の画面へ戻り「終了」で閉じた。

その後の結果:

| 確認項目 | 結果 |
|---|---|
| スイッチ1回で`AbCdE` | 合格 |
| 長押しで連続入力しない | 合格 |
| 離して再押下すると再入力 | 合格 |
| キーが押されたままにならない | 合格 |
| USB抜き差し後も入力できる | 合格 |
| 再接続時に設定アシスタントが再表示されない | 合格 |

`hidutil list`の再取得ログは未提出だが、macOS上で実際に文字入力できたため、IOHID入力経路とInput Reportは実機合格とする。

### 未確認

- test10ファームウェアのWindows回帰確認
- 別のApple Silicon Mac、別ユーザー
- macOS最低対応版
- スリープ復帰
- 長時間連打
- 複数HIDキーボード接続時
- 公開配布用の正式VID:PIDとUSBシリアル番号
- 最終オフラインZIP

## 20. 必須演習の現在状態

| 演習 | 採用 | Windows | macOS |
|---|---|---|---|
| `00_onboard_led_blink` | 必須 | 合格 | 合格 |
| `01_macro_keyboard` | 必須 | 合格 | 合格 |
| `02_rotary_cursor_size` | 必須 | 合格 | 合格 |

`02_rotary_cursor_size`のmacOS版は、ネイティブIOKit HIDホストと非公開CoreGraphicsカーソルAPIを使用する検証実装である。test12でCW／CCW、カーソルサイズ変更、`Ctrl+C`復元を利用者実機確認したため、macOS側の必須演習3本を当該実機では合格とする。USB切断時復元、別Mac・別ユーザー、最低対応macOS、将来互換性は未確認である。

## 21. macOSロータリーカーソル test11・test12実機検証

### 検証環境

```text
macOS: 26.5.2
Architecture: Apple Silicon arm64
Devkit test11: 0.2.0-test11
Devkit test12: 0.2.1-test12
Application VID:PID: 1209:C004
```

`1209:C004`とテスト用シリアル番号はPoC用一時値であり、公開配布用の正式値ではない。

### test11: USB・HID経路

`make flash`で次を確認した。

```text
FLASH: 2280 B / 16 KB
RAM:   208 B / 2 KB
Detected CH32V003
Image written.
Booting
```

実コンパイル行には`-I/usr/include/newlib`が含まれなかった。

`make list`:

```text
Matching devices: 1
VID:PID=1209:C004
Product: UIAP Rotary Cursor macOS Test11
Serial: TEST11-002
```

`make app-dry-run`:

```text
CCW delta=-1
CW delta=1
```

この結果により、GPIO入力、エンコーダーデコード、USB HID Input Report、macOS IOHID受信を合格とした。

### test11: カーソルAPI不合格

```text
Cursor-scale API: PASS current=0.00
Original pointer scale: 0.00
[UIAP-CURSOR-E207] Could not set pointer scale 0.50.
[UIAP-CURSOR-E205] No saved pointer size is available.
```

原因は、非公開カーソルAPIのスカラーABIを64bit型として固定し、32bit `float`値を`0.00`相当へ誤読したことだった。test11はカーソル変更・復元について不合格とする。

### test12修正

- getterの書込み幅から`float32`／`float64` ABIを実行時判定
- 判定したABIでsetterを呼び出す
- 現在値の同値書込みと再読取り自己診断
- NaN、`0.00`、観測範囲外値を状態ファイルへ保存しない
- 変更後と復元後の再読取り検証
- エラー経路での復元試行

### test12結果

利用者から「想定通りの動きをした」との実機報告を受け、直前に案内した検証内容に基づき次を合格とする。

- CW／CCWに応じたカーソルサイズ変更
- `Ctrl+C`終了時の起動前サイズ復元

次は報告またはログがなく未確認である。

- 実機で選択されたABIが`float32`か`float64`か
- USB切断時復元
- 上限・下限での長時間操作
- 別Mac、別ユーザー、最低対応macOS
- スリープ復帰
- 将来のmacOS更新後の互換性
- 最終オフラインZIP

## 24. Windowsダウンロード進捗統合 test13

### 検証ID

```text
WIN-DOWNLOAD-STATIC-001
```

### 対象

```text
uiap-devkit-win64 0.5.0-test13
日付: 2026-08-01
```

### 実装済み

- PowerShellから`curl.exe`を明示的に実行
- `--fail`、`--location`、`--retry 3`、`--retry-delay 2`、`--connect-timeout 30`、`--progress-bar`
- `.part`への取得
- 既存`.part`からの`--continue-at -`
- curl終了コード33時の先頭再取得
- SHA-256一致後の正式名変更
- 不一致ファイルの`.bad-*`隔離
- キャッシュ再利用
- 進捗バーと要約ログの分離
- 固定コンポーネントロック

### 静的検査結果

- ZIPの標準ディレクトリ構造: 合格
- `VERSION`と検証状態表示: 合格
- JSON構文とSHA-256形式: 合格
- 廃止済みトップレベル演習別名がないこと: 合格
- `.cmd`のCRLF、主要ソースのLF: 合格
- `manifest.sha256`整合性: 合格
- 不要な`.git`、ログ、通常ビルド生成物がないこと: 合格

### 未確認

- Windows PowerShell 5.1での実行構文
- Windows 11 x64での実ダウンロード
- xPack GCCの進捗表示
- `Ctrl+C`中断と再開
- curl終了コード33の実動作
- SHA-256不一致隔離の実動作
- 展開済みツールの起動
- `00_onboard_led_blink`のビルド、書き込み、物理点滅
- `01_macro_keyboard`と`02_rotary_cursor_size`の統合
- 別PC、別ユーザー、プロキシ、Windows Defender

したがって、状態は「実装済み・パッケージ静的検査合格・Windows実機未確認」とする。参加者向けリリース合格ではない。

## 25. Windows test14起動不具合とtest15修正

### 検証ID

```text
WIN-START-TEST14-001
WIN-START-TEST15-STATIC-001
```

### test14利用者実機結果

- `path-check.ps1`: PASS
- Devkit版、初期コマンド、初期ディレクトリの案内表示: 成功
- 専用Command Prompt起動: 不合格
- 表示: `'cmd.exe' is not recognized as an internal or external command`
- ダブルクリック時: ウィンドウが一瞬表示されて閉じる

原因は、`start-uiap.cmd`がDevkit用PATH設定後に相対名`cmd.exe`を実行したことと判定した。

### test15実装

- `%SystemRoot%\System32\cmd.exe`を絶対パスで実行
- Windows PowerShell 5.1を絶対パスで実行
- PATHへSystem32、Wbem、Windows PowerShellを明示的に保持
- `doctor`へシステムシェルとPATH保持の検査を追加
- 起動失敗時に`UIAP-E105`、終了コード、実行パスを表示

### 状態

- test14の不具合再現: 利用者実機確認済み
- test15パッケージ静的検査: 合格
- test15ダブルクリック継続起動: 未確認
- test15の`setup`以降: 未確認

## 26. Windows test15 ch32fun SHA-256不一致とtest16修正

### 検証ID

```text
WIN-DOWNLOAD-TEST15-001
WIN-CH32FUN-HASH-TEST15-001
WIN-CH32FUN-TEST16-STATIC-001
```

### test15利用者実機結果

`start-uiap.cmd`から専用Command Promptを継続起動し、`setup`を実行できた。次の取得物は、curl進捗表示、SHA-256検証、展開または配置まで合格した。

- xPack Windows Build Tools 4.4.1-3
- xPack GNU RISC-V Embedded GCC 14.2.0-3
- Python 3.14.6 embeddable x64
- hidapi 0.15.0 for CPython 3.14 Windows x64

ch32funではダウンロード後に`UIAP-E122`となり、次を観測した。

```text
期待値: 37a507fa58710a14dbd3e959def57b02a6b0b1d410c9e307653e22aeb081ba9f
実測値: 30e13fcf4c123981d0fba99a01a31cda30f57757356057bdce2e6cad026f58b1
```

不一致ファイルが`.part.bad-20260801-125444`へ隔離されたため、SHA-256不一致時に正式キャッシュを採用しない処理は実機で確認できた。`setup`全体は未完了である。

### 原因とtest16

Windows版はch32funのZIPを取得していたが、ロックにはmacOS test8で使用したtar.gzのSHA-256が設定されていた。`0.5.3-test16`ではWindows用ZIPの期待値へ修正し、隔離済みファイルを再検証して再利用する処理を追加した。

### 現在状態

- test15の起動継続、curl進捗、主要4取得物: 利用者実機合格
- test15のch32funロック: 不合格
- SHA-256不一致隔離: 利用者実機合格
- test16パッケージ静的検査: 合格
- test16での隔離ファイル再利用、setup完走、doctor、ビルド、書き込み: 未確認

## 2026-08-01 Windows test15 setup完走とtest17 HID演習再統合

### 追加検証記録

| ID | 対象 | 結果 | 状態 |
|---|---|---|---|
| `WIN-SETUP-TEST15-002` | `0.5.2-test15`の起動、Build Tools、GCC、Python、hidapi、ch32fun取得、SHA-256、配置 | 利用者実機で合格 | オンライン`setup`完走を確認 |
| `WIN-HID-PLACEHOLDER-TEST15-001` | `02_rotary_cursor_size`の`make flash` | 利用者実機で不合格 | `UIAP-E240`プレースホルダーにより意図的停止 |
| `WIN-HID-INTEGRATION-TEST17-STATIC-001` | `0.6.0-test17`への演習01・02、ホストアプリ、rv003usb取得定義の統合 | 静的検査合格 | Windows実機のビルド・書き込み・HID動作待ち |

### test15で確認済みの範囲

- `start-uiap.cmd`からCommand Promptが閉じずに起動
- xPack Windows Build Tools 4.4.1-3の取得、SHA-256、展開
- xPack GNU RISC-V Embedded GCC 14.2.0-3の取得、SHA-256、展開
- Python 3.14.6 embeddable x64の取得、SHA-256、展開
- hidapi 0.15.0の取得、SHA-256、配置、import
- ch32fun固定コミットZIPの取得とSHA-256検証
- `setup`完走

### test17の実装範囲

- `01_macro_keyboard`: D5 / PC3、内部プルアップ、押下1回で`AbCdE`、長押し抑止
- `02_rotary_cursor_size`: D8 / PC6=A、GND=C、D9 / PC7=B、Vendor-defined HID、Windowsホストアプリ
- `rv003usb`: コミット`75d926abe89a3002020b989015eab97ce5ad0470`のコア3ファイルとMITライセンス
- 演習内の`make`、`make flash`、`make hidcheck`、`make app-dry-run`、`make app`、`make restore`

### test17で未確認

- Windows実機でのrv003usb取得完走
- 3演習の実コンパイルとリンク
- UIAPduinoへの書き込み
- `01_macro_keyboard`のUSB列挙と文字入力
- `02_rotary_cursor_size`のHID受信、カーソルサイズ変更、終了時復元
- rv003usbファイル単位SHA-256の正式固定

過去PoCの合格結果を、test17再統合版の合格として転記しない。

## 2026-08-01 Windows test17マクロビルドと書き込みコマンド不具合

### 検証ID

```text
WIN-DOCTOR-TEST17-001
WIN-MACRO-BUILD-TEST17-001
WIN-FLASH-COMMAND-TEST17-001
WIN-FLASH-COMMAND-TEST18-STATIC-001
```

### test17利用者実機結果

`uiap-devkit-win64` `0.6.0-test17`で`doctor`を実行し、次を確認した。

- `PASS=37 WARN=3 FAIL=1`
- Build Tools、RISC-V GCC、Python、hidapi、ch32fun、rv003usb、必須演習ファイルを検出
- 3演習の`make -n build`がPASS
- ロータリーカーソルホスト自己診断がPASS
- FAILは`ch32fun.mk`のNewlib判定1件

実際のマクロキーボードのコンパイル行には`-I/usr/include/newlib`がなかった。このFAILは未使用の`NEWLIB?=/usr/include/newlib`定義を検出した診断誤判定とする。

`01_macro_keyboard`の`make flash`では、コンパイルとリンクに成功した。

```text
FLASH: 2484 B / 16 KB
RAM:    228 B / 2 KB
```

生成物としてELF、BIN、外部領域BIN、HEX、LST、MAPを作成した。rv003usbの`#warning "CH32V003"`は既知警告であり、ビルド失敗ではない。

minichlinkは次を確認した。

- VID:PID `1209:B803`
- CH32V003検出
- Flash Storage 16 kB
- Read protection disabled

ただし実行コマンドは次の状態だった。

```text
minichlink -c 0x1209b803 -w   -b
```

書き込みファイルと書き込み領域が欠落したため、minichlinkがUsageを表示し、終了コード255で停止した。`Image written.`と`Booting`は表示されておらず、書き込み成功として扱わない。

### 原因

3演習のMakefileが、自動変数`$<`を含む`FLASH_COMMAND`を`:=`で定義したため、Makefile読込み時に空へ展開された。

### test18修正と静的結果

`0.6.1-test18`では次を行った。

- `FLASH_COMMAND =`へ変更し、`$<`をレシピ実行時に展開
- 3演習の`make -n flash`で対象BINと`flash -b`を確認
- Newlib診断を`make -n build`の実効コンパイル行へ変更
- test17のMarkdownに含まれた制御文字と壊れたWindowsパスを修正
- ZIP、manifest、JSON、UTF-8 BOM、改行、制御文字を静的検査

静的dry-runでは次を確認した。

```text
-w onboard_led_blink.bin flash -b
-w macro_keyboard.bin flash -b
-w rotary_cursor_size.bin flash -b
```

### 現在状態

- test17マクロキーボードのビルド: 利用者実機合格
- test17書き込みコマンド: 利用者実機不合格
- test17 Newlib診断: 誤判定
- test18書き込みコマンドと診断修正: 静的検査合格
- test18の実書き込み、USB列挙、`AbCdE`入力: 未確認
- test18のロータリーHIDとカーソル変更: 未確認

## 2026-08-01 Windows test18必須演習とカーソル適用不具合

### 検証ID

```text
WIN-MACRO-TEST18-001
WIN-ROTARY-HID-TEST18-001
WIN-CURSOR-APPLY-TEST18-001
WIN-CURSOR-APPLY-TEST19-STATIC-001
```

### 利用者実機結果

`uiap-devkit-win64` `0.6.1-test18`について、Windows 11 x64で次の報告を得た。

#### `01_macro_keyboard`

```text
結果: OK
```

ビルド、書き込み、USB HIDキーボード入力を合格として記録する。期待文字列、長押し抑止、再押下などの個別ログは今回未取得のため、過去の検証結果を超えて断定しない。

#### `02_rotary_cursor_size`

`make app-dry-run`は合格した。対象`1209:C004`を1台検出し、エンコーダーのCW／CCW入力を受信できた。

`make app`は次まで成功した。

```text
Matching devices: 1
VID:PID=1209:C004
Product: UIAP RE12000 Cursor Test
Serial: TEST7-001
Original pointer size: 80
Mode: apply
```

最初のサイズ適用時に次で停止した。

```text
[WinError 6] ハンドルが無効です。
make: *** [Makefile:38: app] Error 1
```

この結果から、USB列挙、hidapiオープン、HID受信は合格、Windowsポインターサイズ適用は不合格とする。

### 原因

test18は`CursorBaseSize`更新後に`SystemParametersInfoW(SPI_SETCURSORS, ...)`を呼び出していた。プロジェクトの過去の`03_pot_cursor_haptic` v1.0.6でも同じ`WinError 6`を確認し、v1.0.7で同呼出しを除去していた。test18は既知不具合の回帰である。

### test19修正と静的結果

`0.6.2-test19`では次を実装した。

- `SPI_SETCURSORS (0x0057)`の呼出しを除去
- 過去のWindows 11 x64実機PoCで確認した`0x2029`方式へ変更
- `CursorBaseSize`とアクセシビリティ側`CursorSize`のスナップショット保存・復元
- test17／test18形式の保存状態移行
- stale stateの起動前自動復元
- `make cursor-test`追加
- ホスト自己診断へサイズ段階、スライダー変換、旧状態移行検査を追加
- doctorへ`0x2029`、`SPI_SETCURSORS`回帰、2系統保存対象の静的検査を追加

Python構文、ホスト自己診断、manifest、ZIP整合性、UTF-8、改行を静的確認した。

### 現在状態

- test18 `01_macro_keyboard`: 利用者実機合格
- test18 `02_rotary_cursor_size`のHID列挙と`make app-dry-run`: 利用者実機合格
- test18 `make app` Windowsサイズ適用: 利用者実機不合格
- test19修正: 静的検査合格
- test19 `02_rotary_cursor_size`のビルド、書き込み、HID列挙、CW／CCW、Windowsサイズ変更、`Ctrl+C`復元: 利用者実機合格
- test19の`make restore`単独確認、`make cursor-test`単独確認、USB切断時復元、強制終了後復元: 未確認

## 2026-08-01 Windows test19ロータリーカーソル統合動作

### 検証ID

```text
WIN-ROTARY-CURSOR-TEST19-001
```

### 対象

```text
uiap-devkit-win64 0.6.2-test19
workspace/exercises/02_rotary_cursor_size
Windows 11 x64
```

### 利用者実機結果

`make flash`でファームウェアのコンパイル、リンク、BIN生成、USBブートローダー経由の書き込みが成功した。

```text
FLASH: 2248 B / 16 KB
RAM:    208 B / 2 KB
VID:0x1209, PID:0xb803
Detected CH32V003
Image written.
Booting
```

`rv003usb.S`の`#warning "CH32V003"`は表示されたが、リンク、書き込み、実動作が成功しているため既知警告として扱う。

`make app`では次を確認した。

```text
Matching devices: 1
VID:PID=1209:C004
Product: UIAP RE12000 Cursor Test
Serial: TEST7-001
Original pointer size: 80
Mode: apply
```

エンコーダー操作に応じ、ポインターサイズが16単位で増減した。今回のログでは64～176の範囲でCW／CCWの両方向を確認した。

```text
CW: 96
CW: 112
CW: 128
CW: 144
CW: 160
CW: 176
CCW: 160
CCW: 144
CCW: 128
CCW: 112
CCW: 96
CCW: 80
CCW: 64
```

`Ctrl+C`終了時には起動前のサイズ80へ復元した。

```text
Stopping.
Restored pointer size: 80
```

### 判定

- ファームウェアビルド: 合格
- `1209:B803`経由の書き込み: 合格
- `1209:C004`アプリケーション列挙: 合格
- hidapiによるデバイスオープン: 合格
- CW受信: 合格
- CCW受信: 合格
- Windowsポインターサイズ変更: 合格
- `Ctrl+C`終了時の起動前サイズ復元: 合格
- test18の`WinError 6`回帰修正: test19で利用者実機合格

`1209:C004`、`TEST7-001`はPoC用一時値であり、正式な公開配布用識別子としての採用を意味しない。

### 引き続き未確認

- `make restore`単独実行による異常終了後復元
- `make cursor-test`単独実行
- USB切断時の終了と復元
- 強制終了後の復元
- USB再接続後の再起動
- 高速回転時の取りこぼし
- 長時間連続操作
- 別のWindows 11 PC、別ユーザー
- 最終オフライン参加者向けZIP

---

## 2026-08-01 センタースイッチ付きロータリーエンコーダーモジュール実機確認

### 対象

- 部品: `GND / S1 / S2 / KEY / 5V`表記のセンタースイッチ付きロータリーエンコーダーモジュール
- 共通配線: GND→GND、S1→D8 / PC6、S2→D9 / PC7、KEY→D5 / PC3、5V→5V
- 演習: `01_macro_keyboard`、`02_rotary_cursor_size`
- OS: Windows、macOS

### 利用者実機結果

- Windowsの`01_macro_keyboard`: 想定どおり動作
- Windowsの`02_rotary_cursor_size`: 想定どおり動作
- macOSの`01_macro_keyboard`: 想定どおり動作
- macOSの`02_rotary_cursor_size`: 想定どおり動作

### 判定

- 独立モメンタリスイッチと3端子ロータリーエンコーダーから、新モジュール1個への置き換え: 合格
- 5本の共通配線による両演習の切り替え: 合格

---

## 2026-08-01 `01_macro_keyboard`共通実装の静的確認

### 変更

- `win/`と`mac/`の重複実装を削除
- `macro_keyboard.c`、`usb_config.h`、`funconfig.h`、`host/hidcheck.py`を演習直下へ統合
- macOS互換のHID DescriptorとHID Boot Keyboard制御要求処理を共通実装へ採用
- TinyUSBヘッダー依存を除去

### 結果

- Windows同梱RISC-Vツールチェーンによるビルド: 合格
- FLASH: 2460 B / 16 KB
- RAM: 220 B / 2 KB
- 共通ファームウェアのWindows実機入力: 利用者実機合格
- 共通ファームウェアのmacOS実機入力: 利用者実機合格

### 実機追認

共通化コミット`c261cfa`後、同じ共通ファームウェアをWindowsとmacOSで確認し、両方で想定どおり動作することを利用者実機で確認した。これにより、`01_macro_keyboard`のOS別ソース廃止と単一実装への統合を合格とする。

---

## 2026-08-01 `00`・`02`共通実装の静的確認

### 変更

- `00_onboard_led_blink`のOS別ファームウェアとMakefileを単一実装へ統合
- `02_rotary_cursor_size`のOS別ファームウェア、USB設定、Makefileを単一実装へ統合
- `02`の共通HIDレポートを`[delta, sequence]`の2バイトへ統一
- `02`のOS固有ホストだけを`host/win`、`host/mac`へ移動

### 結果

- 共通`00`ビルド: 合格、FLASH 436 B / 16 KB、RAM 0 B / 2 KB
- 共通`02`ビルド: 合格、FLASH 2340 B / 16 KB、RAM 200 B / 2 KB
- 共通`00`のWindows/macOS実機点滅: 再確認待ち
- 共通`02`のWindows/macOS HID入力・ポインターサイズ変更・復元: 再確認待ち

---

## 2026-08-05 USB HID事前診断のWindows実機確認

### 検証ID

`WIN-PREFLIGHT-HID-001`

### 対象

- ソース: `workspace/preflight`
- ソーススナップショット: コミット`1dbff6d`
- ボード: UIAPduino Pro Micro CH32V003 V1.4
- ホストOS: Windows（詳細な版とビルド番号は未記録）
- minichlink: `38e653f8354ea8fc19da5f2595cf9958d26738e7`
- プロトコル: `1.2`
- ファームウェア: `1.0.2`

### 利用者実機結果

`make flash`でビルドとUSBブートローダー経由の書き込みに成功した。

- FLASH: 2724 B / 16 KB（16.63%）
- RAM: 216 B / 2 KB（10.55%）
- ブートローダー: VID `1209`、PID `B803`
- MCU検出: CH32V003
- 書き込み結果: `Image written.`、`Booting`
- minichlink Part UUID: `e7-ea-ab-cd-50-0c-bc-55`

`rv003usb.S`の`#warning "CH32V003"`は表示されたが、コンパイル、リンク、書き込みは正常に完了した。

続けて`make preflight`を実行し、次の全項目が`PASS`した。

- USB HID列挙: `1209:D003`、`UIAP HID Preflight`
- PCからデバイスへのランダムnonce送信
- デバイスからPCへの同一nonce応答
- プロトコルバージョン: `1.2`
- ファームウェアバージョン: `1.0.2`
- ボード名: `UIAPduino Pro Micro CH32V003 V1.4`
- MCU ID: `e7-ea-ab-cd-50-0c-bc-55`
- 最終結果: `RESULT: PASS`

nonceは実行時に生成された`0xF86A3629`が往復で一致した。HID経由で取得したMCU IDはminichlinkのPart UUIDと一致した。

### 判定

- Windowsでの診断用ファームウェアビルド: 合格
- `1209:B803`経由の書き込み: 合格
- `1209:D003` Vendor-defined HIDへの再列挙: 合格
- PCとUIAPduinoの双方向Feature Report通信: 合格
- プロトコル、ファームウェア、ボード名の整合性検査: 合格
- MCU IDの取得とminichlink表示との一致: 合格
- Windows実機のUSB HID事前診断: 合格

### 当該報告時点で未確認

- macOS実機でのビルド、書き込み、HID列挙、事前診断
- 別のWindows PCおよび別ユーザー
- USBハブ経由
- 長時間または反復実行

macOS実機については、後続の`MAC-PREFLIGHT-HID-001`で動作確認した。

---

## 2026-08-05 USB HID事前診断のmacOS実機確認

### 検証ID

`MAC-PREFLIGHT-HID-001`

### 対象

- ソース: `workspace/preflight`
- ファームウェアソーススナップショット: コミット`1dbff6d`
- ボード: UIAPduino Pro Micro CH32V003 V1.4
- ホストOS: macOS（詳細な版、ビルド番号、Macの機種は未記録）

### 利用者実機結果

利用者から、macOS実機でもUSB HID事前診断が正常に動作したとの報告を受けた。Windowsと同じ`workspace/preflight`のファームウェアおよびホスト診断を使用している。

今回は実行ログを収録していないため、個別のnonce、MCU ID、メモリ使用量、minichlink版は記録しない。

### 判定

- macOS実機でのUSB HID事前診断: 利用者実機合格
- Windows/macOS共通のpreflight実装: 両OSで実機確認済み

### 引き続き未確認

- 別のMacおよび別ユーザー
- macOSの最低対応版と最新対象版を分けた確認
- USBハブ経由
- 長時間または反復実行
