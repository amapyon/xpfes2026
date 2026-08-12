# 決定履歴

この文書は、決定事項、検討中事項、未確認事項、却下事項を区別するために使用する。

新しい決定は日付付きで追記する。過去の記録を無断で書き換えず、変更理由を残す。

> **現行仕様の読み方:** 2026-07-25以降のWindows xPackネイティブ決定、2026-08-01の配布Devkit最終方針、およびそれ以降の日付付き決定を現行仕様とする。これ以前のMSYS2、最終オフライン版、macOS 15対応、当日ネットワーク不要、最終成果物を講師側で決める前提に関する記述は、当時の検証履歴または旧方針として保持する。

---

## 2026-07-19時点の決定事項

### ワークショップ

- XP祭り2026で物理UIの電子工作ワークショップを実施する
- 所要時間は約1.5時間
- 参加者は約8人
- 初心者から経験者まで複数レベルが混在する
- UIAPduino本体は当日配布する
- VS Codeは参加者が事前にインストールする
- 外付けスイッチとロータリーエンコーダを配布予定

### ハードウェア

- 標準ボードはUIAPduino Pro Micro CH32V003 V1.4
- MCUはCH32V003
- PCとの接続には主にUSBを使用する

### 対象OS

- Windows 11 64bit
- macOS Apple Silicon
- 主な実験と検証はWindows 11で行う
- 参加者向け演習は両OSに対応する
- Intel Macは必須対応に含めない

### 配布開発環境

- Windows版: `uiap-devkit-win64.zip`
- macOS版: `uiap-devkit-macarm64.zip`
- 展開後ディレクトリ名も同名に固定
- Windows版の標準環境はMSYS2 UCRT64
- Windows版のMSYS2は`runtime/msys64`へ格納
- macOS版はApple Silicon arm64ネイティブ
- Rosetta 2を必須にしない
- WindowsとmacOSで演習コマンドを可能な限り共通化する

### ディレクトリ

- 外部依存は`workspace/deps`
- 参加者向け演習は`workspace/exercises`
- 参考・発展用PoCは`workspace/poc`
- 共通補助スクリプトはトップレベル`scripts`
- 復旧用バイナリは`firmware`
- ライセンスは`licenses`

### 共通環境変数

- `UIAP_DEVKIT_ROOT`
- `UIAP_WORKSPACE`

### ビルド

- Makefileに開発者固有の絶対パスを記述しない
- `ch32fun`は`$(UIAP_WORKSPACE)/deps/ch32fun`から参照
- `rv003usb`は`$(UIAP_WORKSPACE)/deps/rv003usb`から参照
- 共通ターゲットとして`make`、`make flash`、`make clean`を使用する
- 参加者向け標準手順では追加インストールとインターネット接続を前提にしない

### 検証状態

技術項目は、少なくとも次を区別して記録する。

- 提案
- 実装済み
- ビルド確認済み
- 書き込み確認済み
- USB列挙確認済み
- HID送受信確認済み
- 物理動作確認済み
- Windows確認済み
- macOS確認済み
- 参加者向け採用済み

一段階の成功を、後続段階の成功として扱わない。

---

## 2026-07-19 振動モーターPoCと書き込み方式

### 決定・確認済み

- Windows 11 64bitのMSYS2 UCRT64環境で、UIAPduino Pro Micro CH32V003 V1.4へ`minichlink`を使って書き込みできる
- 書き込み用USBブートローダーのVID:PIDは`1209:B803`
- `minichlink`では`-c 0x1209b803`相当の指定が必要
- 参加者向けの書き込みコマンドは`make flash`へ統一する
- `D6/A2`はCH32V003の`PC4`へ接続され、`TIM1_CH4`としてPWM出力に使用できる
- ドライバー回路内蔵振動モーターモジュールを`5V`、`GND`、`D6/A2`へ接続し、Windows実機で振動を確認した

### USB HID振動モーターPoC

`workspace/poc/vibration_motor_hid`のPoCについて、Windows 11 64bitで次を確認済みとする。

- ファームウェアのビルド
- PC側ユーティリティのビルド
- `1209:B803`ブートローダーによる書き込み
- Vendor-defined USB HID Feature Report
- アプリケーション`1209:D003`としての列挙
- 振動レベル`1`～`100`の受信
- 振動強度の変化
- `status`による設定値取得
- `off`による停止

`1209:D003`はPoC用暫定値であり、公開配布または製品化前に利用可否を確認し、必要なら正式なVID:PIDへ変更する。

macOS Apple Silicon向けのPC側ソースコードとMakefileは存在するが、実ビルド、書き込み、列挙、HID送受信、モーター動作は未検証である。

### 採用状態

- 振動モーターHID制御PoCはWindows向けPoCとして完了
- ワークショップの最終制作物または必須演習としての採用は未決定
- Vendor-defined HID Feature Report、Report ID、振動レベル範囲を最終仕様へ採用するかは未決定

---

## 2026-08-02 振動モーターHID PoCのmacOS検証

### 確認済み

`workspace/poc/vibration_motor_hid`の構成変更後の実装について、利用者のmacOS Apple Silicon実機で次を確認した。

- ファームウェアのビルド
- `1209:B803`ブートローダーによる書き込み
- アプリケーションUSB HIDとしての動作
- PC側からの振動モーター制御
- 振動モーターの物理動作

検証IDは`MAC-HID-MOTOR-001`とする。Windows検証済みの状態と合わせ、このPoCの両対象OSにおける基本動作確認を完了とする。

### 変更しない決定

- ワークショップの最終制作物または必須演習としての採用は未決定
- Vendor-defined HID Feature Report、Report ID、振動レベル範囲の最終採用は未決定
- `1209:D003`はPoC用暫定値のままとする

---

## 移行状況

### 確認済み

次の移行先が存在することを確認済み。

```text
C:\pj\uiap-devkit-win64\runtime\msys64
C:\pj\uiap-devkit-win64\workspace\deps\ch32fun
C:\pj\uiap-devkit-win64\workspace\deps\rv003usb
C:\pj\uiap-devkit-win64\workspace\poc
```

`workspace/poc`で確認済みのディレクトリ:

```text
hscroll_encoder_poc
touchpad_pinch_poc
vibration_motor_hid
```

### 移行未完了

単純PWM制御に使用した`vibration_motor_poc`は、次の旧配置で動作確認された。

```text
C:\pj\uiap-devkit-win64\workspace\vibration_motor_poc
```

標準配置は次である。

```text
workspace/poc/vibration_motor_poc
```

必要なら旧PoCを標準位置へ移動し、Makefileの依存参照を`UIAP_WORKSPACE`ベースへ変更する。当時は参加者向け配布版への収録を保留していたが、2026-08-12の決定により収録対象とした。

---

## 検討中

- ワークショップで最終的に制作するUSBデバイス
- USB HIDクラスの具体的な用途
- HID Usage
- 演習の最終構成
- 振動モーターHID PoCを参加者向け演習へ採用するか
- キックスタートを実装するか
- 参加者が使用する振動レベルの範囲
- macOS Apple Siliconでの振動モーターHID PoC実機検証
- macOS版RISC-Vツールチェーンの最終採用とオフライン同梱方式（検証基準はxPack 14.2.0-3）
- macOS版の書き込みツールと書き込み方式
- 使用するVS Code拡張機能
- 配布する電子部品の最終構成
- 当日のネットワーク接続を前提とするか
- ブートローダーおよび復旧用ファームウェアの配布範囲
- ブートローダー破損時の復旧手順と必要機材
- `runtime`をどこまで最小化するか
- macOS向けコード署名または公証
- Intel Macへの任意対応
- 公開配布時のアプリケーションVID:PID

---

## 明示的に未決定

- USBメディアコントローラーを制作物にすること
- 振動モーターコントローラーを最終制作物にすること
- 特定のHID Usageへの固定
- Vendor-defined Feature Reportを最終方式に固定すること
- `1209:D003`を公開配布用VID:PIDとして採用すること
- Intel Macを必須対応にすること
- ワークショップ当日にインターネット接続を必須にすること

---

## 2026-07-24

### 検証済み

- Windows 11 x64で、xPack Windows Build Tools、xPack GNU RISC-V GCC、
  ch32fun、rv003usb、minichlinkを使用したオンライン・ブートストラップ型
  開発環境が動作した
- `make clean`、`make`、`make flash`を実行し、UIAPduino Pro Micro
  CH32V003 V1.4への書き込みと実機動作を確認した
- Windows形式パスは、MakefileからPOSIXシェルへ渡す前に
  `C:/...`形式へ正規化する必要がある
- モメンタリスイッチをD5へ接続したHIDキーボードを確認した
- ロータリーエンコーダーをD8、D9、GNDへ接続し、
  Vendor-defined HID経由でWindowsホストアプリへ回転量を送信できた
- PythonホストアプリがHIDレポートを受信し、
  Windowsのポインターサイズを変更できた

### 影響

- Windows版のMSYS2 UCRT64標準構成と、今回検証した
  xPackネイティブ構成の比較が必要
- MakefileにWindowsパス正規化規則を追加する
- 書き込み対象数は物理USB親デバイス単位で判定する
- PowerShellからPythonを実行するときは、複雑な `python -c` を使用せず、
  Pythonファイルを実行する

### 検討中

- Windows版標準環境をxPackベースのネイティブ構成へ変更すること
- ロータリーエンコーダーによるポインターサイズ変更を
  ワークショップ演習として採用すること

### 未確認

- オフライン環境
- 別PCおよび別ユーザー
- macOS Apple Silicon
- 複数UIAPduinoの同時接続
- USBシリアル番号のMCU固有ID化

### PoC限定

- `1209:C003`、`1209:C004`は一時的なアプリケーションVID/PID
- `TEST3-001`、`TEST7-001`は一時的なUSBシリアル番号


## 2026-07-25 Windows標準構成とch32fun参加者向けサブセット

### 決定

- Windows版の標準構成は、MSYS2を使用しないxPackベースのWindowsネイティブ構成とする
- 参加者向け`workspace/deps/ch32fun`は、固定済み上流コミットから許可リスト方式で生成する
- 完全な上流ツリーから不要ディレクトリを手作業または削除リストだけで除く方式を、最終リリースの標準にしない
- 許可リストに記載した相対パスだけを、新しい空ディレクトリへコピーする
- 上流MIT `LICENSE`、上流コミット、サブセット識別情報、実際の許可リストを参加者向けサブセットへ残す
- 完全な固定コミットの上流ソース、許可リスト、生成スクリプト、検査スクリプト、ローカルパッチ、再生成手順を対応ソースとして別途保持する
- SBOMでは`ch32fun`を完全版ではなく参加者向けサブセットとして識別する

### 初期除外方針

次は参加者向けサブセットへ原則として含めない。

```text
.github/
build_scripts/
examples/
examples_ch5xx/
examples_h41x/
examples_l103/
examples_usb/
examples_v10x/
examples_v20x/
examples_v30x/
examples_x00x/
examples_x035/
projects/
platformio.ini
package.json
.git/
```

採用演習で必要になった場合は、ディレクトリ全体ではなく必要ファイルを個別に許可し、理由と検証結果を記録する。

### 理由

- UIAPduino Pro Micro CH32V003 V1.4で使用しない他MCU向けサンプルによる混乱を減らす
- 参加者向けZIPのファイル数、展開時間、セキュリティスキャン、ライセンス監査の対象を減らす
- 手作業による削除漏れと必要ファイルの誤削除を防ぐ
- 上流更新時に意図しない新規ファイルが参加者向けZIPへ混入することを防ぐ
- 配布物の来歴、再生成性、SBOM、対応ソースの整合性を維持する

### 影響

- `15_CH32FUN_SUBSET_RULES.md`を追加する
- `10_DEVKIT_STRUCTURE.md`、`20_BUILD_RULES.md`、`50_RELEASE_CHECKLIST.md`、`60_TROUBLESHOOTING.md`、`70_VALIDATION_RESULTS.md`を更新する
- リリース元に許可リスト、生成スクリプト、検査スクリプト、上流情報、パッチ管理を追加する
- WindowsとmacOSの全採用演習をサブセットで再検証する
- 過去のMSYS2標準構成の記録は履歴として残すが、現行標準としては本決定が優先する

### 未確認

- 許可リストの最終ファイル一覧
- 生成スクリプトと検査スクリプトの実装
- Windows 11 x64でのサブセット全演習検証
- macOS Apple Siliconでのサブセット全演習検証
- 最終オフラインZIP
- 対応ソースアーカイブとSBOMの生成
- サブセット化による実際のZIPサイズ、展開時間、スキャン時間の削減量

---


## 2026-07-25 PC側Pythonプログラムの演習内配置

### 決定

- PC側Pythonプログラムは、対応する演習の`host`ディレクトリへ配置する
- 標準パスは`workspace/exercises/<exercise-name>/host/<program>.py`とする
- トップレベルの`workspace/host`は使用しない
- PC側プログラムがない演習には、空の`host`ディレクトリを作成しない
- 各演習の`make app`は、同じ演習の`host`だけを参照する
- `scripts/python`には、Devkit全体で使用する診断、USB列挙、復旧などの補助プログラムだけを配置する

### 理由

- ファームウェア、Makefile、参加者向けREADME、PC側プログラムを演習単位で完結させる
- 演習の追加、削除、配布対象選択を容易にする
- ホストアプリと対応ファームウェアのVID:PID、Usage、Report形式の不一致を防ぐ
- 別演習のホストアプリを誤って起動する可能性を減らす
- 参加者向けZIPから未採用演習を除外するときに、関連ホストアプリも同時に除外できるようにする

### 影響

- ロータリーエンコーダー演習の標準配置は次とする

```text
workspace/exercises/02_rotary_cursor_size/host/<platform>/cursor_size_host.py
```

- `10_DEVKIT_STRUCTURE.md`、`20_BUILD_RULES.md`、`40_WORKSHOP_GUIDE_RULES.md`、`50_RELEASE_CHECKLIST.md`、`60_TROUBLESHOOTING.md`、`70_VALIDATION_RESULTS.md`を更新する
- `99_FULL_PROJECT_GUIDE.md`を分割文書から再生成する
- Devkit本体では、旧`workspace/host/cursor_size_host.py`を新しい標準位置へ移し、Makefileとコマンドラッパーを修正する必要がある

### 検証状態

- ディレクトリ構成と文書規約: 決定済み
- Devkit本体のファイル移設: 未確認
- 移設後の`make app`: 未確認
- 移設後のHID受信とWindowsポインターサイズ変更: 未確認
- 移設後の`Ctrl+C`終了と設定復元: 未確認

### 過去の検証記録

Devkit `0.3.2-test7`のWindows実機検証では、次の旧配置を使用した。

```text
workspace/host/cursor_size_host.py
```

過去の検証結果は履歴として保持し、標準配置へ移設後に再検証する。

---

## 2026-07-25 GPIO直結パッシブブザーPoCの上限

### 決定

- 対象をUIAPduino Pro Micro CH32V003 V1.4、`12085P`、D6/A2（PC4 / TIM1_CH4）の追加部品なし直結PoCに限定する
- ファームウェアとホスト側の上限を次に固定する

```c
#define MAX_TONE_DURATION_MS  2000u
#define MAX_TOTAL_TONE_MS     2000u
#define DIRECT_DUTY_DIVISOR   2u
#define DIRECT_COOLDOWN_MS    5000u
```

- 連続発音と1 PLAYコマンド内の総発音時間は2,000msを上限とする
- PWM通電デューティ比は50%を上限とする
- 発音後は5,000msのクールダウンを強制する
- 上限を超える時間、デューティ比、短いクールダウンは採用しない

### 利用者実機報告

- ブザーを5Vへ接続した構成で発音した
- 2,000msの連続発音で明確な問題は確認されなかった
- 50%デューティ比で明確な問題は確認されなかった
- この結果は利用者の実機報告であり、GPIO電流、PC4端子電圧、誘導性スパイク、温度の測定結果ではない

### 位置付け

- 本決定は主催者用PoCのソフトウェア上限である
- GPIO直結を一般に許可する決定ではない
- 5V接続がCH32V003の端子定格へ適合することを確認した決定ではない
- 参加者向け必須演習、標準回路、長期利用としての採用は未決定かつ現時点では不可とする
- `30_HARDWARE_RULES.md`のGPIO直接接続と誘導性負荷に関する一般規則を変更しない

### 次の検証

- GPIOピーク電流と平均電流
- PC4のHigh-Z期間を含む最高・最低電圧
- PWM切替時の誘導性スパイク
- MCU、レギュレーター、ブザーの温度
- 2秒発音の反復耐久
- 複数のUIAPduinoとブザー個体
- WindowsとmacOSでの更新版ビルド、書き込み、USB HID、発音

---


## 2026-07-26 ポテンショメーター＋ポインターサイズ＋振動統合PoC

### 現行実装

- 演習ディレクトリは`workspace/exercises/03_pot_cursor_haptic`
- 実機確認済みリビジョンは`v1.0.8`
- 対象OSはWindows 11 x64
- RV09 B10Kポテンショメーター値を0～1023としてVendor-defined HIDでPCへ送る
- Windowsポインターサイズを32～256の15段階へ変更する
- サイズ変更成功時に振動モーターモジュールでクリック感を出す
- 振動既定値はレベル4、80msを2回、間隔40msとする
- 振動レベルは0～5からホスト起動時に選択できる

### 確認済み配線

- ポテンショメーター両端: +5V、GND
- ワイパー: 68kΩ/100kΩ分圧、0.1µF、D1/A0（PA2/A0）
- 5V基準: 68kΩ/100kΩ分圧、0.1µF、D0/A1（PA1/A1）
- 振動モジュールIN: D6/A2（PC4）
- 振動モジュール電源: +5V、GND、100µF追加
- 5VワイパーをADCへ直接接続しない

### ADC安定化

v1.0.8では次を現行方式とする。

- チャンネル切替後の先頭2回を破棄
- 16回測定から最大値と最小値を除外して平均
- 5点中央値と低域フィルタ
- 3カウントの報告値デッドバンド
- 12カウントの段階ヒステリシス
- 隣接段階は3サンプル連続で確定
- モーター駆動中と停止後50msはADC更新停止

利用者実機で、ADC値によるポインターサイズのふらつきが解消したことを確認した。

### Windowsホスト処理

- `make doctor`、`make hidcheck`、`make adc-monitor`、`make cursor-test`、`make haptic-test`、`make app`を提供する
- 起動前の`CursorBaseSize`と`Accessibility\\CursorSize`を保存する
- stale restore stateがある場合はアプリ起動前に復元する
- Windows 11 x64の即時サイズ反映に使用する`SystemParametersInfoW`アクション`0x2029`は未文書化であり、このPoCに限定する
- 公開仕様またはWindows更新で動作が変わる可能性があるため、各リリース候補で`make cursor-test`を実行する

### 一時識別子

```text
VID:PID: 1209:D003
Usage Page: 0xFF00
Usage: 0x0001
Product: UIAP Pot Cursor Haptic
Serial: POT-HAPTIC-001
```

正式な公開配布用VID:PID、製品名、USBシリアル番号としては未決定である。

### 検証状態

- Windowsビルド: 確認済み
- FLASH 3428 B、RAM 252 B: 確認済み
- USBブートローダー書き込み: 確認済み
- HID列挙と送受信: 確認済み
- ADC読取り: 確認済み
- Windowsポインターサイズ変更: 確認済み
- 振動レベル4: 確認済み
- ADC安定化v1.0.8: 確認済み
- macOS相当実装: 未実装
- ワークショップ必須演習への採用: 未決定

### 位置付け

- Windows 11 x64向け統合PoCとして主要動作合格
- PoC合格を最終参加者向け採用済みとは扱わない
- macOSを含む共通演習へ採用する場合は、macOS側ポインター設定またはOS非依存の別成果物を設計する
- 正式VID:PID、複数個体、長時間、USB切断、強制終了、スリープ復帰、最終オフラインZIPを追加検証する

---


## 2026-07-26 Windows版Devkitの展開先パス制約

### 決定

- Windows版Devkitのルートは、ローカルドライブ上のASCII・空白なしパスに限定する
- 使用できる文字は半角英数字、ドット、ハイフン、アンダースコアとする
- 推奨展開先は`C:\uiap\uiap-devkit-win64`または`C:\pj\uiap-devkit-win64`とする
- 空白、全角文字、その他の非ASCII文字、UNCパスを含む場所は非対応とする
- 非対応パスでは`UIAP-E103`を表示し、`setup`前に停止する
- `start-uiap.cmd`、`setup.ps1`、`doctor.ps1`で同じ規則を検査する

### 理由

- GNU Makeの`include`は、展開後の空白を複数ファイルの区切りとして扱う
- `ch32fun.mk`を含むビルド全体で、ソース、インクルード、リンカースクリプト、リダイレクト先を完全に空白対応させる変更は影響範囲が大きい
- 全角文字はPowerShell、GNU Make、xPack `sh.exe`、RISC-V GCC間の文字コード互換性を保証できない
- 当日の安定性と復旧容易性を、任意パス対応より優先する

### 採用しない対策

- 8.3短縮パスへの依存
- `subst`ドライブを参加者へ作成させる方式
- Devkitを自動的に別場所へコピーする方式
- Makefileの一部だけへ引用符を追加して対応済みとすること

### 影響

- 事前案内で推奨展開先を指定する
- `README.md`、`10_DEVKIT_STRUCTURE.md`、`20_BUILD_RULES.md`、`40_WORKSHOP_GUIDE_RULES.md`、`50_RELEASE_CHECKLIST.md`、`60_TROUBLESHOOTING.md`、`70_VALIDATION_RESULTS.md`を更新する
- `99_FULL_PROJECT_GUIDE.md`を再生成する
- Windowsリリース候補では、ASCIIパスでの成功と非対応パスでの早期停止を両方検証する

### 検証状態

- 利用者による空白・全角パスでのsetup失敗報告: 確認済み
- 原因調査と対策実装: 完了
- 対策版`0.4.2-test10`の静的検査、ZIP CRC、内部マニフェスト: 合格
- Windows実機での`UIAP-E103`表示と推奨パスでの再セットアップ: 未確認

---

## 2026-07-26 展開先パスエラーの日本語表示

### 決定

- 参加者向けの展開先パスエラーは日本語で表示する
- `UIAP-E103`などのエラーコードは変更しない
- 原因、現在の場所、利用できない条件、推奨移動先、再起動手順を表示する
- `start-uiap.cmd`、`setup.ps1`、`doctor.ps1`の各経路で日本語表示する
- 英語だけの復旧案内を参加者向け標準にしない

### 理由

- 英語のエラーメッセージを理解できない参加者がいる可能性がある
- エラーコードだけでは、フォルダー移動とコンソール再起動の必要性を判断できない
- ワークショップ中の講師への質問と誤った自己修正を減らす

### 検証状態

- 空白を含むパスで`UIAP-E103`が表示されること: 利用者実機確認済み
- 全角文字を含むパスで`UIAP-E103`が表示されること: 利用者実機確認済み
- 日本語表示版`0.4.3-test11`の静的検査、ZIP CRC、内部マニフェスト: 合格
- 日本語表示版のWindows実機確認: 未確認

## 2026-07-26 展開先パス検査の回帰不具合と訂正

### 新しい決定

- Windows版Devkitは、条件を満たす複数階層のローカルパスを許可する
- 各フォルダー名は半角英数字、ドット、ハイフン、アンダースコアだけとし、空白を含めない
- `C:\pj\xpfes2026\uiap-devkit-win64`は有効な展開先とする
- `UIAP-E103`は、空白、非ASCII文字、UNCパスなど、実際に非対応のパスだけに使用する
- パス判定は`scripts/path-check.ps1`へ集約する
- `setup.ps1`と`doctor.ps1`に同じ正規表現を重複実装しない
- 有効パスと非対応パスの自動テストをリリース必須項目とする
- 日本語エラーメッセージの方針は維持する

### 訂正対象

Devkit `0.4.3-test11`は、有効な次のパスを`UIAP-E103`で拒否した。

```text
C:\pj\xpfes2026\uiap-devkit-win64
```

原因は次の正規表現である。

```powershell
'^[A-Za-z]:\[A-Za-z0-9_.\-]+$'
```

この実装はWindowsのバックスラッシュと複数階層を正しく表現していない。

### 影響

- `0.4.3-test11`をWindows版リリース候補として使用しない
- 有効なパスで`UIAP-E103`が表示された場合、参加者へフォルダー移動を案内しない
- 修正版Devkitへ切り替える
- `20_BUILD_RULES.md`、`40_WORKSHOP_GUIDE_RULES.md`、`50_RELEASE_CHECKLIST.md`、`60_TROUBLESHOOTING.md`、`70_VALIDATION_RESULTS.md`を更新する
- `99_FULL_PROJECT_GUIDE.md`を再生成する

### 検証状態

- 有効パスでの誤拒否: 利用者実機確認済み
- 原因特定: 完了
- 文書訂正: 完了
- パス判定コードの修正: 未実施
- 修正版の有効パス実機確認: 未確認
- 修正版の空白、全角、UNC拒否確認: 未確認

### 過去決定との関係

2026-07-26の「Windows版Devkitの展開先パス制約」と「展開先パスエラーの日本語表示」は、非対応パスの方針と日本語表示について引き続き有効である。

ただし、`0.4.2-test10`および`0.4.3-test11`の判定実装が正しいという記録は、本項で訂正する。複数階層のASCII・空白なしパスは拒否対象ではない。

---

## 2026-07-27 演習ディレクトリへの移動とコマンド体系

### 決定

- `start-uiap.cmd`または`start-uiap.command`起動後、受講者自身が`cd`コマンドで対象演習ディレクトリへ移動する
- Windows版の初期ディレクトリは`workspace`とする
- 演習移動用の`sample`、`macro`、`blink`などのトップレベルコマンドを廃止する
- 特定演習用の`cursorapp`、`cursorlist`、`cursorrestore`、`hidcheck`などのトップレベルコマンドも廃止する
- `cursorstore`は標準コマンド名として採用しない
- 演習固有操作は、対象演習ディレクトリ内のMakefileターゲットへ統一する
- Devkit共通のトップレベルコマンドは`setup`、`doctor`、`versions`、`report`などに限定する

### 標準操作例

Windows Command Prompt:

```text
cd /d "%UIAP_WORKSPACE%\exercises\02_rotary_cursor_size"
make hidcheck
make app
make list
make restore
```

macOS:

```sh
cd "$UIAP_WORKSPACE/exercises/02_rotary_cursor_size"
make hidcheck
make app
make list
make restore
```

### 理由

- 受講者が現在の演習と実行ディレクトリを把握できる
- WindowsとmacOSで、標準的な`cd`と`make`を学べる
- グローバル別名と演習Makefileの機能重複をなくせる
- 演習の追加・削除時にトップレベルラッパーを増減する必要がない
- 間違った演習のホストアプリやVID:PIDを操作する可能性を減らせる
- 手順書、README、Makefileを演習単位で完結させられる

### 影響

- Windows Devkitから`sample.cmd`、`macro.cmd`、`blink.cmd`、`cursorapp.cmd`、`cursorlist.cmd`、`cursorrestore.cmd`を削除する
- グローバル`hidcheck.cmd`が特定演習のVID:PIDを既定値にする構成を廃止する
- `welcome.cmd`とトップレベルREADMEには、演習一覧と`cd`例を表示する
- 各演習READMEは、最初に対象ディレクトリへの`cd`を記載する
- 各演習Makefileは、必要な`make hidcheck`、`make app`、`make list`、`make app-dry-run`、`make restore`を提供する
- `50_RELEASE_CHECKLIST.md`で旧ラッパー不在を検査する

### 検証状態

- 根拠文書の更新: 完了
- Devkit本体の旧ラッパー削除: 未実施
- Windows 11 x64での`cd`から各演習を実行する確認: 未確認
- macOS Apple Siliconでの確認: `00_onboard_led_blink`への`cd`、`make clean`、`make flash`を確認済み。他演習は未確認
- Devkit `0.4.4-test12`: 旧ラッパーを含むため本決定へ未適合

---

## 2026-07-29 macOS Apple Silicon Devkit主催者検証

### 決定

- macOS版の主催者検証用ベースラインを`uiap-devkit-macarm64` `0.1.7-test8`とする
- この版はオンライン初期化型の検証版であり、参加者向け最終版として配布しない
- macOS版はApple Silicon arm64ネイティブとし、Rosetta 2を使用しない
- 参加者向け最終版では、Homebrew、Xcode Command Line Tools、システムPython、管理者権限、当日のインターネット接続を要求しない
- 主催者が`minichlink`を生成する`build-minichlink`は主催者専用とし、検証用MacではXcode Command Line Toolsを使用してよい
- GNU MakeはDevkit内へ配置し、参加者向けコマンド名を`make`へ統一する
- システムの`/usr/bin/make`へフォールバックしない
- RISC-Vツールチェーンの検証基準をxPack GNU RISC-V Embedded GCC 14.2.0-3 arm64とする
- `ch32fun`と`rv003usb`はWindowsと同じ固定コミットを使用する
- `minichlink`は固定済み`ch32fun`ソースとlibusb 1.0.29からarm64ネイティブで生成し、libusbを静的リンクする
- ローカル生成した`runtime/bin/minichlink`だけを対象に隔離属性を除去し、その後にアドホック署名と署名検証を行う
- Devkit全体への再帰的な隔離属性削除、Gatekeeper全体の無効化、`sudo spctl --master-disable`は標準手順にしない
- `doctor`でarm64、動的ライブラリ依存、隔離属性、コード署名、ビルド来歴を検査する
- `doctor`でリリース阻害項目が残る場合は`UIAP-E299`で失敗させる

### 利用者実機確認済み

検証環境:

```text
macOS: 26.5.2
Architecture: Apple Silicon arm64
Rosetta: not detected
Devkit: 0.1.7-test8
Distribution: Online Bootstrap Test
```

確認済み:

- `start-uiap.command`起動
- Devkitルート、環境変数、初期`workspace`の設定
- オンライン`setup`
- GNU Make 4.4.1 arm64
- xPack RISC-V GCC 14.2.0-3 arm64
- `ch32fun`コミット`1e4887e11d4bfa739ed5604524b69f5be9f9275b`
- `rv003usb`コミット`75d926abe89a3002020b989015eab97ce5ad0470`
- `build-minichlink`によるlibusb 1.0.29の静的ビルド
- `minichlink`バージョン識別子`38e653f8354ea8fc19da5f2595cf9958d26738e7`
- `minichlink`のMach-O arm64、静的libusb、システムフレームワークのみの動的依存
- `minichlink`単体の隔離属性除去、アドホック署名、署名検証
- `doctor`結果`PASS=32 WARN=1 FAIL=1`
- `00_onboard_led_blink`のビルド
- FLASH 444 B、RAM 0 B
- ELF、BIN、HEX、LST、MAP生成
- USBブートローダー`1209:B803`の検出
- CH32V003の検出
- `make flash`による書き込みと`Booting`
- 基板上LEDの0.2秒点灯・0.8秒消灯

実機ログで観測した入力・成果物SHA-256:

```text
ch32fun source archive: 37a507fa58710a14dbd3e959def57b02a6b0b1d410c9e307653e22aeb081ba9f
libusb 1.0.29 archive: 5977fc950f8d1395ccea9bd48c06b3f808fd3c2c961b44b0c2e6e29fc3a70a85
minichlink binary: 56515fb09d3d3f5d44f747f37bee6aee004e65e3cc4c41ab2dedae0cd738121e
```

これらは当該実機実行で観測した値である。最終リリース用固定値および再現ビルド保証としては、別途`bootstrap.lock`、SBOM、対応ソース、リリース手順へ正式反映して再検証する。

### 回帰不具合と訂正

- `0.1.0-test1`: 未署名・未公証のためGatekeeperの個別許可が必要
- `0.1.1-test2`: Devkitルートを親`Downloads`と誤認するため使用しない
- `0.1.2-test3`: パス解決を修正したが、`/usr/bin/make`依存のため最終候補にしない
- `0.1.3-test4`: Devkit内GNU Makeへ変更し、Lチカのビルドまで確認
- `0.1.4-test5`: `minichlink`導入方式の検討版。最終方式にしない
- `0.1.5-test6`: `build-minichlink`初版。GNU Makeの`otool -L`先頭行を依存パスと誤検出
- `0.1.6-test7`: `otool -L`誤検出を修正。生成した`minichlink`へ隔離属性が継承され、`Killed: 9`となる問題を確認
- `0.1.7-test8`: `minichlink`単体の隔離属性除去、アドホック署名、署名検証を自動化し、書き込みとLED物理動作まで確認

### 書き込み時の確認事項

`Error: Could not initialize b003boot programmer`は、`minichlink`が実行できてもUSBブートローダー待機状態を捕捉できない場合に発生する。今回の実機では、RESETを押したままUSBを接続し、RESETを離して直ちに`make flash`を再実行することで成功した。

この一度の再試行結果だけを根拠に自動復旧を実装しない。参加者向け手順では、ブートローダーモード、USBケーブル、直結、接続台数、待機時間を順に確認する。

### 未確認・リリース阻害

- Devkit内Pythonとhidapi
- HID送受信とホストアプリ
- 最終レビュー済みch32fun許可リスト
- `ch32fun`およびlibusb入力アーカイブSHA-256の正式固定
- `-I/usr/include/newlib`への暗黙依存の除去確認
- ネットワーク切断状態
- 最終オフラインZIP
- Developer ID署名・公証の採否
- 別のApple Silicon Mac、別ユーザー
- macOS 15の最低対応環境での検証
- 参加者向け採用

### Gatekeeper方針

- 検証版の起動ファイルについては、対象ファイルと入手元を確認した上でmacOS標準の個別許可を使用する
- 主催者がローカル生成した`minichlink`に隔離属性が継承された場合は、その`minichlink`単体だけを処理対象とする
- 隔離属性除去後にアドホック署名を付け、`codesign --verify`で検証する
- Devkit全体への再帰的な`xattr -dr`を標準手順にしない
- Gatekeeper全体を無効化しない
- 最終参加者向け版でDeveloper ID署名・公証するか、個別許可を正式手順とするかは未決定

## 2026-07-31 必須演習とmacOS test10検証

### 決定

- ワークショップの必須演習を次の3本とする
  - `00_onboard_led_blink`
  - `01_macro_keyboard`
  - `02_rotary_cursor_size`
- `01_macro_keyboard`の標準配線はD5 / PC3とGNDの間のモメンタリスイッチとする
- `02_rotary_cursor_size`の標準配線はD8 / PC6=A、GND=C、D9 / PC7=Bとする
- macOSのHID Boot Keyboardは、Device Descriptorのクラス値を`0`とし、Interface DescriptorでHIDクラスを宣言する
- Boot Keyboardの`GET_REPORT`、`GET_IDLE`、`SET_IDLE`、`GET_PROTOCOL`、`SET_PROTOCOL`を処理する
- macOS初回接続時にキーボード設定アシスタントが識別キーを要求した場合、Mac本体のキーを代用せず、前の画面へ戻って「終了」で閉じる
- macOS 26.5.2の確認環境では「スキップ」ボタンがなかったため、「スキップしてANSIを選択」を標準手順にしない
- `0.1.9-test10`を、LチカとHIDマクロキーボードを確認した当時の最新macOS主催者検証版とする

### 実機確認済み

`01_macro_keyboard`について、macOS Apple Siliconで次を確認した。

- キーボード設定アシスタントを「終了」で閉じた後、スイッチ1回で`AbCdE`
- 長押しで連続入力しない
- 離して再度押すと再入力する
- キーが押されたままにならない
- USB抜き差し後も入力できる
- 再接続時に設定アシスタントは再表示されない

### test9の訂正

`0.1.8-test9`は、macOSでUSB Device `1209:C003`として列挙したが、Device Descriptorの`bDeviceClass = 3`によりIOHIDデバイスとして列挙されず、文字入力できなかった。同じ書き込み済みデバイスはWindowsで`AbCdE`を入力できた。

また、test9の`doctor`はNewlib依存なしと判定したが、実際のコンパイル行に`-I/usr/include/newlib`が残っていた。このPASS判定を訂正し、test10で元オプション除去と必須演習3本のdry-run検査を追加した。

### 影響

- 以前の「演習の最終構成は未決定」という記録は、必須演習3本の選定について本決定で更新する
- ワークショップで最終的に制作するUSBデバイス、最終HID Usage、公開用VID:PIDは引き続き未決定である
- `01_macro_keyboard`の参加者向けmacOS手順へキーボード設定アシスタントの終了方法を追加する
- `doctor`の静的検査だけでHID実機合格としない
- Newlib検査は必須演習ごとの実際のMake dry-runを使用する

### 未確認・リリース阻害

- `02_rotary_cursor_size`のmacOS実機動作
- 非公開CoreGraphicsカーソルAPIを参加者向け方式として採用するか
- `0.1.9-test10`マクロキーボードのWindows回帰確認
- 最終レビュー済み`ch32fun`許可リスト
- `rv003usb`入力SHA-256の正式固定
- ネットワーク切断状態と最終オフラインZIP
- 別のApple Silicon Mac、別ユーザー、macOS最低対応版
- Developer ID署名・公証または正式な個別許可方針



## 2026-07-31 macOSロータリーカーソル test11・test12

### 決定

- macOS Apple Silicon向け最新主催者検証版を`uiap-devkit-macarm64` `0.2.1-test12`とする
- `02_rotary_cursor_size`は、macOS 26.5.2の当該実機では必須演習として合格とする
- macOSホストはIOKit HIDを使用し、Python・hidapiを要求しない
- 非公開カーソルAPIのスカラー型を固定せず、getterの書込み幅から`float32`／`float64` ABIを実行時判定する
- カーソルAPI自己診断に失敗した場合は設定変更を開始しない
- 不正な現在値を状態ファイルへ保存しない
- 設定変更後と復元後は再読取りで検証する
- 正常終了時の復元を必須動作とする

### 実機確認済み

`0.2.0-test11`で次を確認した。

- `1209:C004`のUSB・IOHID列挙
- 製品名`UIAP Rotary Cursor macOS Test11`
- CW／CCW HID Input Report
- 実コンパイル行に`-I/usr/include/newlib`がない

一方、test11はカーソル倍率を`0.00`と誤読し、変更`E207`と復元`E205`に失敗したため、カーソル制御機能は不合格とする。

`0.2.1-test12`ではABI判定と安全な保存・復元を修正した。利用者実機報告により次を確認した。

- CW／CCWに応じたカーソルサイズ変更
- `Ctrl+C`終了時の起動前サイズ復元

### 影響

- 以前の「`02_rotary_cursor_size`のmacOS実機動作は未確認」という現在状態は、本記録で更新する
- 必須演習3本はmacOS 26.5.2の当該Apple Silicon実機で合格となる
- 非公開APIの正式採用可否は、実機合格とは別の決定事項として残す
- test11はUSB・HID入力の検証履歴として保持するが、カーソル変更用には使用しない
- 参加者向け手順では`make list`、`make app-dry-run`、`make host-doctor`、`make app`の順に確認する

### 未確認・リリース阻害

- USB切断時の自動復元
- 別のApple Silicon Mac、別ユーザー
- 最低対応macOSと最新対象macOSでの回帰
- スリープ復帰
- 非公開CoreGraphicsカーソルAPIを参加者向け正式方式として採用するか
- 公開APIだけで実現できる代替方式
- 最終レビュー済み`ch32fun`許可リスト
- `rv003usb`入力SHA-256の正式固定
- ネットワーク切断状態と最終オフラインZIP
- Developer ID署名・公証または正式な個別許可方針

---
## 決定更新テンプレート

```markdown
## YYYY-MM-DD

### 決定
- 

### 理由
- 

### 影響
- 

### 検討中
- 

### 却下・未採用
- 
```

## 2026-08-01 Windows大容量ダウンロード進捗方式

### 決定

- Windowsオンライン初期化型Devkitの標準ダウンロード方式を、PowerShell補助スクリプトからWindows標準の`curl.exe`を明示的に実行する方式とする
- PowerShellの`curl`別名は使用しない
- 標準引数は`--fail`、`--location`、`--retry 3`、`--retry-delay 2`、`--connect-timeout 30`、`--progress-bar`とする
- ダウンロード中は`runtime/downloads/<archive>.part`へ保存する
- `.part`がある場合は`--continue-at -`で再開を試みる
- curl終了コード33の場合は再開非対応として`.part`を削除し、先頭から1回取得し直す
- curl終了コード0かつSHA-256一致をダウンロード完了条件とする
- SHA-256一致後だけ正式キャッシュ名へ変更する
- SHA-256不一致ファイルは`.bad-<timestamp>`へ隔離する
- ダウンロード定義は固定ロックファイルへ集約する
- 進捗バーの制御文字をセットアップログへ保存しない
- 最終参加者向けオフライン版では大容量ダウンロードを発生させない方針を維持する

### 理由

- xPack GNU RISC-V Embedded GCCなどの取得中に、停止しているのか進行しているのかを初心者が判断できる
- macOSのcurl方式との差異を小さくできる
- Windows 11標準機能で実現し、追加バイナリとライセンス監査対象を増やさない
- 再試行、再開、リダイレクト、終了コードを小さい実装で扱える
- `.part`とSHA-256検証により、不完全アーカイブを正式キャッシュとして展開しない

### 実装

- `uiap-devkit-win64` `0.5.0-test13`をオンライン初期化型の主催者検証版として生成した
- test13は`setup`、`doctor`、`versions`、`report`、固定ロック、ダウンロード共通関数、Lチカ演習骨格を含む
- test13の`ch32fun`は最終許可リストではなくテスト用サブセットである
- 入力Devkitの検証済みUSB演習ソースが提供されていないため、`01_macro_keyboard`と`02_rotary_cursor_size`は未検証コードを生成せず、`UIAP-E240`で停止するプレースホルダーとした
- 必須演習3本の決定は変更しない

### 検証状態

- パッケージ静的検査: 合格
- Windows 11 x64実機でのダウンロードと進捗表示: 未確認
- 中断再開、ハッシュ不一致、プロキシ環境: 未確認
- Lチカのビルド、書き込み、物理動作: 未確認
- 必須HID演習2本の統合: 未確認
- 参加者向け最終オフラインZIP: 未確認

### 未採用

- `Invoke-WebRequest`を標準ダウンローダーにする案
- BITSを標準方式にする案
- `aria2c`をDevkitへ追加同梱する案
- ブラウザ手動保存を通常セットアップ手順にする案

これらは追加の版差、Windows専用状態管理、バイナリ追加、保存先誤操作などが増えるため、標準方式には採用しない。ブラウザ手動取得は、将来必要になった場合も明示的な復旧手順として別途検証する。

## 2026-08-01 Windows起動シェルの絶対パス化

### 決定

- Windows版Devkitは、専用Command Promptを`%SystemRoot%\System32\cmd.exe`の絶対パスで起動する
- Windows PowerShell 5.1は`%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe`の絶対パスで起動する
- Devkit用PATHへSystem32、Wbem、Windows PowerShellを明示的に保持する
- 起動失敗時はエラーを表示して一時停止し、ダブルクリックしたウィンドウを即時終了させない
- `doctor`はシステムシェル実体とPATH保持を検査する

### 理由

`0.5.1-test14`で、パス検査と案内表示後に相対名`cmd.exe`を解決できず、専用Command Promptへ移行できないことを利用者実機で確認したため。

### 実装

`uiap-devkit-win64` `0.5.2-test15`へ反映した。

### 検証状態

- test14不具合: 利用者実機確認済み
- test15静的検査: 合格
- test15ダブルクリック継続起動、`setup`、ダウンロード、ビルド、書き込み: 未確認

## 2026-08-01 取得アーカイブ形式とSHA-256の一体管理

### 決定

- 外部取得物は、版またはコミットだけでなく、URL、保存ファイル名、アーカイブ形式、SHA-256の組として固定する
- 同じコミットのZIPとtar.gzでSHA-256を共有しない
- ロックの形式またはハッシュを変更した場合は、新しいDevkit版として検証する
- `0.5.2-test15`はch32funのロック不整合があるため使用しない
- 修正版を`0.5.3-test16`とする

### 根拠と参照先

- 一般規則: `20_BUILD_RULES.md`
- ch32fun固有値: `15_CH32FUN_SUBSET_RULES.md`
- 実機結果: `70_VALIDATION_RESULTS.md`
- 復旧手順: `60_TROUBLESHOOTING.md`
- リリース検査: `50_RELEASE_CHECKLIST.md`

### 検証状態

- test15の不具合と不一致隔離: 利用者実機確認済み
- test16静的検査: 合格
- test16のWindows実機setup完走以降: 未確認

## 2026-08-01 Windows test17への必須HID演習再統合

### 決定

- Windowsオンライン初期化型の次版を`uiap-devkit-win64` `0.6.0-test17`とする
- `01_macro_keyboard`と`02_rotary_cursor_size`の`UIAP-E240`プレースホルダーを削除し、実装済みソースを配置する
- `01_macro_keyboard`はD5 / PC3とGNDのスイッチで`AbCdE`を入力する
- `02_rotary_cursor_size`はD8 / PC6、GND、D9 / PC7のエンコーダー入力をVendor-defined HIDでWindowsホストへ送る
- ホストアプリは`workspace/exercises/02_rotary_cursor_size/host`へ配置する
- rv003usbはコミット`75d926abe89a3002020b989015eab97ce5ad0470`へ固定する
- test17では固定コミットRaw URLから必要なコアファイルを取得し、実測SHA-256を記録する
- 最終参加者向け版ではrv003usbの期待SHA-256を固定し、原則としてオフライン同梱する

### 維持する未決定事項

- `1209:C003`、`1209:C004`を正式な公開配布用VID:PIDとして採用すること
- `TEST3-001`、`TEST7-001`を正式なシリアル番号として採用すること
- test17を参加者向け最終版とすること

### 検証状態

- パッケージ・ソース統合の静的検査: 合格
- Windows実機のビルド、書き込み、USB列挙、HID動作: 未確認
- 過去のWindows PoCとmacOS test10/test12の実機結果は参考履歴として保持するが、test17の合格判定には流用しない

## 2026-08-01 Windows test18書き込みコマンド修正

### 決定

- `uiap-devkit-win64` `0.6.0-test17`は、HID演習のビルド検証用履歴として保持するが、書き込み可能なリリース候補として使用しない
- 修正版を`0.6.1-test18`とする
- ch32funの`cv_flash`へ渡す`FLASH_COMMAND`は、自動変数`$<`を使用する場合、遅延評価`=`で定義する
- `doctor`は必須演習3本の`make -n flash`を検査し、対象BINと`flash -b`が揃わない場合はFAILとする
- Newlib依存は未使用変数定義ではなく、`make -n build`の実効コンパイル行で判定する
- 参加者向けテキストの制御文字検査をリリース検査へ追加する

### 根拠

Windows実機で`01_macro_keyboard`はFLASH 2484 B、RAM 228 Bまでビルドできたが、書き込みコマンドが`-w -b`相当となり、minichlinkがUsageを表示して終了した。原因は`FLASH_COMMAND :=`による`$<`の早期展開である。

同じ実機ログではコンパイル行にNewlibインクルードがないにもかかわらず、`doctor`が未使用の既定値を検出してFAILにした。

### 検証状態

- test17ビルドと不具合再現: 利用者実機確認済み
- test18の3演習書き込みコマンドdry-run: 静的検査合格
- test18のWindows実書き込み、USB列挙、HID動作: 未確認
- test18を参加者向け最終版とすること: 未決定

## 2026-08-01 Windows test19ポインターサイズ反映修正

### 決定

- `uiap-devkit-win64` `0.6.1-test18`は、`02_rotary_cursor_size`のWindowsポインターサイズ変更機能に使用しない
- 修正版を`0.6.2-test19`とする
- Windowsポインターサイズ変更で`SPI_SETCURSORS (0x0057)`を使用しない
- 現行PoCでは、Windows 11 x64で過去に実機確認した`SystemParametersInfoW`アクション`0x2029`を使用する
- 起動前の`CursorBaseSize`と`Software\Microsoft\Accessibility\CursorSize`を保存し、正常終了と`make restore`で復元する
- 旧版の保存状態を移行し、異常終了後のstale stateを次回起動前に復元する
- HID入力とWindows設定変更を分離する`make cursor-test`を標準確認ターゲットへ追加する
- `doctor`とリリース検査で`SPI_SETCURSORS`の再導入をFAILにする

### 根拠

Windows test18では`make app-dry-run`が成功し、HID受信まで正常だったが、`make app`の最初のサイズ適用で`WinError 6`となった。プロジェクト内には、`03_pot_cursor_haptic` v1.0.6で同じ不具合を確認し、v1.0.7で修正した履歴がある。

### 制約

`0x2029`はMicrosoft公開仕様に記載されていない未文書化動作である。正式な公開APIとして保証せず、Windows 11 x64向けPoCに限定する。Windows更新、別PC、別ユーザーごとに`make cursor-test`を実行する。将来、公開APIだけで同等の即時変更を実現できる方法が確認できた場合は置き換えを再検討する。

### 検証状態

- test18 HID受信と不具合再現: 利用者実機確認済み
- test19実装と静的検査: 合格
- test19 `02_rotary_cursor_size`のビルド、`1209:B803`経由書き込み、`1209:C004`列挙、CW／CCW受信、Windowsポインターサイズ変更: 利用者実機確認済み
- test19 `Ctrl+C`終了時の起動前ポインターサイズ復元: 利用者実機確認済み
- test18で発生した`SPI_SETCURSORS`由来の`WinError 6`は、test19で解消確認済み
- Windows版の必須HID演習`01_macro_keyboard`と`02_rotary_cursor_size`は、現行test18/test19系で基本動作を利用者実機確認済み
- `make restore`単独確認、`make cursor-test`単独確認、USB切断・強制終了時復元、別Windows PC、最終オフラインZIP: 未確認
- test19を参加者向け最終版とすること: 未決定

---

## 2026-08-01 配布用Devkit作成前の最終方針更新

### 決定

- Windows版の現行標準は、MSYS2を使用しないxPackベースのWindowsネイティブ構成とする。過去のMSYS2/UCRT64記述は検証履歴としてのみ残し、現行手順、Makefile、起動処理、リリース判定へ混用しない。
- 最終参加者向けDevkitもオンライン・ブートストラップ方式とする。初回`setup`ではインターネット接続を使用し、固定URL、固定バージョン、アーカイブ形式、SHA-256で入力を管理する。
- Devkitのバージョン番号は`MAJOR.MINOR.PATCH`の3桁だけで管理する。`-rc1`、`-testN`などの接尾辞を使用しない。
- macOS版にもPythonとhidapiを含める。当時の`02_rotary_cursor_size`ネイティブarm64ホスト自体がPython/hidapiへ依存しないこととは区別する。このホスト方式は2026-08-11の共通Pythonホスト決定で更新済みである。
- `ch32fun`の許可リスト方式と`rv003usb`の配布形態は、現在採用している形式を維持する。
- Windowsの`SystemParametersInfoW`アクション`0x2029`とmacOSの非公開CoreGraphics APIは、互換性リスクを明記し、各リリースで回帰検証することを条件に今回の参加者向けDevkitでの使用を許容する。
- macOSの正式対応範囲はApple SiliconのmacOS 26以降とする。macOS 15はサポート対象外とする。
- 参加者向け`firmware/`へ含めるのは、通常使用するものと、講師が当日に行う簡易復旧に必要なものに限定する。専用機材を使う深い復旧用資材は別管理してよい。

### 判断保留

- Windows版とmacOS版それぞれの最終BOM。必要性と内容を整理した後に確定する。
- アプリケーションUSBの正式VID:PID、Product文字列、Serial文字列。現行のPoC値を正式値とは扱わない。
- macOSのDeveloper ID署名・公証を行うか、個別許可方式を正式運用とするか。

### リリースへの影響

- 「最終オフラインZIP」「ネットワーク切断状態」は今後のリリース必須条件から外す。過去の未確認記録は履歴として残す。
- オンライン最終版では、ダウンロード失敗、SHA-256不一致、途中再実行、正常キャッシュ再利用をリリース検査へ含める。
- macOS 15での検証は不要となり、macOS 26以降の複数環境での回帰確認を対象とする。
- USB識別子を確定した時点で、ファームウェア、ホストアプリ、列挙スクリプト、README、検証記録を同一リリース内で更新する。

---

## 2026-08-01 必須HID演習の入力部品統合

### 決定

- `01_macro_keyboard`の独立したモメンタリスイッチと、`02_rotary_cursor_size`の3端子ロータリーエンコーダーを廃止する
- 両演習で[センタースイッチ付きロータリーエンコーダーモジュール](https://electronicwork.shop/items/64b9e54b9dd503007bc60458)を1個共用する
- モジュール基板の表記に合わせ、GND→GND、S1→D8 / PC6、S2→D9 / PC7、KEY→D5 / PC3、5V→5Vとする
- `01_macro_keyboard`はKEYだけを読み、`02_rotary_cursor_size`はS1/S2だけを読む
- 演習を切り替えるときも5本の配線は変更しない
- 販売ページに記載された仕様は動作電圧5V、1周20パルスとして参加者向け資料に明記する

### 影響

- GPIO番号とHID機能は変わらない
- ファームウェア内の信号名をモジュール表記のKEY、S1、S2へ合わせる
- 旧部品で得た実機検証結果は履歴として保持する

### 検証状態

- 2026-08-01に、新モジュールを共通配線した`01_macro_keyboard`と`02_rotary_cursor_size`がWindows、macOSとも想定どおり動作することを利用者実機で確認した
- 新モジュールへの入力部品統合: 合格

---

## 2026-08-01 `01_macro_keyboard`のWindows/macOS共通化

### 決定

- `01_macro_keyboard`の`win/`と`mac/`を廃止し、ファームウェア、USB設定、列挙確認スクリプト、Makefileを演習直下の単一実装へ統合する
- macOS test10で必要になったDevice Descriptorのクラス値0、Interface DescriptorでのHID宣言、HID Boot Keyboard制御要求への応答を共通実装の基準とする
- 共通USB設定からmacOS側だけに存在したTinyUSBヘッダー依存を除き、配布中のrv003usbとch32funだけで両OSからビルドできるようにする
- USB Productを`UIAP Macro Keyboard`、Serialを`TEST3-001`へ統一する。いずれもPoC用一時値とする
- OS差は同一Makefile内の環境変数とツールパスで吸収し、ソースを複製しない

### 根拠

- `01_macro_keyboard`にはOS固有のホストアプリケーションがない
- 旧`win/host/hidcheck.py`と`mac/host/hidcheck.py`は同一内容だった
- HIDキーボードのUSBプロトコルとGPIO動作はOS非依存であり、macOS互換DescriptorはWindowsでも規格どおり使用できる

### 検証状態

- 共通ファームウェアのWindows同梱ツールチェーンによるビルド: 合格
- 共通化コミット`c261cfa`後のWindows実機入力: 利用者実機合格
- 共通化コミット`c261cfa`後のmacOS実機入力: 利用者実機合格
- `01_macro_keyboard`のWindows/macOS共通化: 合格

---

## 2026-08-01 `00_onboard_led_blink`と`02_rotary_cursor_size`の共通化

### 決定

- `00_onboard_led_blink`の`win/`と`mac/`を廃止し、ファームウェアとMakefileを演習直下へ統合する
- 基板上LEDはPC0のアクティブLowとして、0.2秒点灯・0.8秒消灯を共通動作とする
- `02_rotary_cursor_size`のファームウェア、USB設定、Makefileを演習直下へ統合する
- `02_rotary_cursor_size`の共通HIDレポートはReport IDなしの`[delta, sequence]` 2バイトとする
- WindowsホストとmacOSホストはいずれも先頭バイトを移動量として読み、2バイト目の診断用連番を無視する
- OS固有のポインター設定処理だけを`02_rotary_cursor_size/host/win`と`host/mac`へ保持する
- 共通USB Productを`UIAP Rotary Cursor`、Serialを`TEST7-001`とする。いずれもPoC用一時値とする

### 根拠

- LチカのGPIO処理とファームウェア書き込み方式はOSに依存しない
- ロータリーエンコーダーのGPIOデコードとVendor-defined HID送信はOSに依存しない
- WindowsホストはmacOS test13の2バイトレポートを正しく処理できることを実機確認済みである
- `02`でOS差が必要なのはWindowsとmacOSのポインター設定APIだけである

### 検証状態

- 共通`00`ファームウェアのWindows同梱ツールチェーンによるビルド: 合格
- 共通`02`ファームウェアのWindows同梱ツールチェーンによるビルド: 合格
- 共通化後のWindows/macOS実機動作: 利用者実機合格

---

## 2026-08-11 必須HID演習の段階配線

### 決定

- 2026-08-01の5本共通配線を改め、参加者向けの現行標準は段階配線とする
- `01_macro_keyboard`ではGND→GND、KEY→D5 / PC3の2本だけを接続する
- PC3の内部プルアップを使用するため、`01`ではS1、S2、5Vを接続しない
- `02_rotary_cursor_size`へ進むとき、USBを外してS1→D9 / PC7、S2→D8 / PC6、5V→5V（赤い配線）の3本を追加する
- `02`の5V接続は、UIAPduinoのマイクロコントローラー電源が初期状態の5V設定であることを前提とする

### 根拠

- 同じモジュールと既存の共通ファームウェアを使用し、GND/KEYの2本だけで`01_macro_keyboard`が従来どおり動作することを利用者実機で確認した
- 接続本数を2本から5本へ増やすことで、センタースイッチ入力から2相信号による回転検出へ段階的に学習できる
- S1をD9、S2をD8へ割り当てることで、指定モジュールとUIAPduino間の配線が交差しない
- ファームウェアはS1をPC7、S2をPC6へ割り当て直す。S1/S2の論理上の順序は維持するため、回転方向の定数とHID処理は変更しない

### 検証状態

- `01_macro_keyboard`のGND/KEY 2本配線: 利用者実機合格
- `02_rotary_cursor_size`の3本追加後の再確認: 既存の5本配線実績あり。段階手順としての再確認待ち

---

## 2026-08-11 `04_rotary_cursor_haptic`の必須演習追加

### 決定

- 振動なしの`02_rotary_cursor_size`は従来の独立した必須演習として維持する
- `02_rotary_cursor_size`の内容を新しい`04_rotary_cursor_haptic`へコピーし、振動による触覚フィードバックだけを`04`へ追加する
- `04`ではドライバー回路内蔵の5V振動モーターモジュールを使用し、VCC→5V、GND→GND、IN→D6/A2 / PC4とする
- 今回の`04`では振動モジュールのVCC-GND間コンデンサーを追加せず、モーター本体をGPIOへ直接接続しない
- `04`のUSB識別子は暫定VID:PID `1209:C005`、Product `UIAP Rotary Haptic`、Serial `TEST8-001`とする
- `04`のHID入力を`[Report ID 1, delta, sequence]`とし、触覚指示にはFeature Report `[Report ID 2, 1]`を使用する
- ホストアプリがOSのカーソルサイズを変更して再読取りに成功した時だけ、約60msの振動を指示する
- 上限／下限、`make app-dry-run`、カーソル変更失敗時は振動させない
- 起動時はPC4をLowとし、指示後はファームウェア側のタイマーで必ずLowへ戻す

### 根拠

- 振動なしのカーソル演習と触覚追加演習を分離し、参加者が機能追加の差分を段階的に理解できる
- USB識別子と状態ファイルを分けることで、`02`のファームウェアや復元状態との取り違えを検出しやすくする
- 既存の`vibration_motor_hid` PoCで、PC4とドライバー内蔵5V振動モジュールによる制御をWindows/macOSで確認済みである

### 検証状態

- `02_rotary_cursor_size`の振動追加前状態への復元: 完了
- Windows同梱ツールチェーンによる`02`ビルド: 合格（Flash 2,340 bytes、RAM 200 bytes）
- Windows同梱ツールチェーンによる`04`ビルド: 合格（Flash 2,640 bytes、RAM 204 bytes）
- `02`と`04`のWindows/macOSホストPython構文検査: 合格
- `02`の従来プロトコル自己テストと`04`の入力Report ID・触覚コマンド自己テスト: 合格
- 4演習のWindows/macOS配布キット生成を含む既存テスト11件: 合格
- `04_rotary_cursor_haptic`のWindows/macOS実機動作: 再確認待ち

---

## 2026-08-11 `02_rotary_cursor_size`ホストのWindows/macOS共通化

### 決定

- `host/win/cursor_size_host.py`と`host/mac/cursor_size_host.py`を廃止し、`host/cursor_size_host.py`へ統合する
- HID列挙、デバイス選択、レポート解釈、イベントループ、終了時復元、CLIを共通処理とする
- ポインター設定処理だけを`WindowsCursorBackend`と`MacCursorBackend`へ分離し、実行時にOSを選択する
- コマンドを`list`、`hidcheck`、`dry-run`、`app`、`restore`、`cursor-test`、`self-test`、`version`へ統一する
- WindowsのJSON状態ファイルと旧形式移行、macOSの倍率状態ファイルは従来形式を維持する
- この時点では`04_rotary_cursor_haptic`を統合対象外として`host/win`と`host/mac`を維持した。後続の「`04_rotary_cursor_haptic`ホストのWindows/macOS共通化」で更新済みである

### 根拠

- USB HIDプロトコルと操作手順は両OSで同一であり、OS差はポインター設定APIへ限定できる
- 共通処理を一か所にすることで、修正時のWindows/macOS間の差異と配布漏れを減らせる
- 既存の状態ファイル形式を維持すれば、更新前に保存された復元情報を継続利用できる

### 検証状態

- Python構文検査: 合格
- Windowsバックエンドのプロトコル、サイズ変換、状態移行自己テスト: 合格
- Windowsでのバージョンコマンド: 合格
- Windows/macOS配布ZIPの構成を含む既存テスト11件: 合格
- 同梱MakeとPythonによる`host-doctor`および主要ターゲット展開: 合格
- Windows実機での統合後ホストの想定動作: 利用者実機合格
- macOS実機での現行演習の基本動作: Devkit `v0.1.2`で利用者実機合格

---

## 2026-08-11 `04_rotary_cursor_haptic`の触覚パターン変更

### 決定

- 回転中はカーソルサイズだけを変更し、振動させない
- 最後の回転から200ms経過した後、通常変更ではレベル95の80msパルスを間隔40msで2回返す
- 上限／下限では、最後の回転から200ms後にレベル95の250msパルスを1回返す
- 200ms以内に次の回転が来た場合は、保留中の結果と待ち時間を最後の入力で更新する
- Feature Reportのコマンド`1`を通常変更、`2`を上限／下限として使用する

### 根拠

- エンコーダーの機械的なクリックと振動を時間的に分離する
- 弱い振動モジュールでも、ダブルパルスと長いパルスの違いを知覚しやすくする

### 検証状態

- ホストの遅延・再スケジュールと2コマンドの自己テストを追加
- ファームウェアの500Hz PWMとパターン状態機械を追加
- 変更前のレベル90版は、Windows実機での統合動作を利用者報告により合格
- 現行レベル95・一括パターン版は、Windows実機での統合動作を利用者報告により合格
- macOS実機での統合動作は再確認待ち

---

## 2026-08-11 `03`・`04`の触覚パターン実行部共通化

### 決定

- Feature Reportを`[Report ID, level, on_ms LE16, off_ms LE16, count]`の7バイトへ統一する
- ホストはLEVEL、ON時間、OFF時間、回数を1回のレポートで送信する
- 03と04は同一の`haptic_pattern.h`と`haptic_pattern_protocol.h`を持ち、500Hz PWM、繰り返し、パターン置換、自動停止を同じ実装で処理する
- `level=0`を即時停止、`count=0`かつ`level>0`を`make on`用の連続動作、`count>=1`を有限パターンとする
- 03の`make pulse`からホスト側の待機と後続OFF送信を除き、デバイス側自動停止へ変更する
- 03へ`make pattern LEVEL=<1..100> ON_MS=<1..5000> OFF_MS=<0..5000> COUNT=<1..255>`を追加する
- 04の通常変更は`95, 80ms, 40ms, 2回`、上限／下限は`95, 250ms, 0ms, 1回`を送る

### 根拠

- 03と04のデバイス側制御を共通化し、演習間の実装差と保守負担を減らす
- USBやホストOSのスケジューリングに依存せず、デバイス側の1ms処理で振動時間と自動停止を保証する
- パターン変更時にファームウェアの再書き込みを不要にする

### 検証状態

- 両ホストのPython構文検査とFeature Report自己テスト: 合格
- 両ファームウェアのクロスコンパイラ構文検査: 合格
- 共通ヘッダーのバイト一致検査を配布構成テストへ追加
- Windows実機での新プロトコル動作: 03・04とも利用者報告により合格
- macOS実機での新プロトコル動作: 再確認待ち

---

## 2026-08-11 `00_onboard_led_blink`の3連フラッシュ化

### 決定

- 基板上LEDを150ms点灯・150ms消灯で3回点滅させ、その後1.5秒消灯するパターンを繰り返す
- 参加者向け成功条件を「短く3回点滅してから長く休止する」へ変更する
- 工場出荷時の単発周期点滅との判別を、この3回のまとまりで行う

### 根拠

- 単発点滅の周期だけを変更しても、工場出荷時ファームウェアとの区別がつきにくい
- 3連フラッシュは短時間で確認でき、初心者にも口頭と文章で説明しやすい

### 検証状態

- クロスコンパイラ構文検査: 合格
- パターン定数の回帰検査を追加
- Windows実機での3連フラッシュ: 極性修正後に利用者確認で合格
- macOS実機での3連フラッシュ: 再確認待ち

### LED極性の訂正

Windows実機で休止期間が点灯する症状を確認したため、基板上LEDの定義を`PC0`のアクティブHighへ訂正する。`FUN_HIGH`を点灯、`FUN_LOW`を消灯とする。過去のアクティブLowという記録は、この訂正前の履歴として扱う。

極性修正後の3連フラッシュは、Windows実機で利用者確認により合格した。macOS実機は再確認待ちとする。

---

## 2026-08-11 必須4演習の`hidcheck`出力統一

### 決定

- `01`〜`04`の`make hidcheck`を、`Matching devices`、`VID:PID`、`Product`、`Serial`、Product名付きPASS行の同一形式へ統一する
- VID/PIDに一致するデバイスがちょうど1台であることに加え、Product文字列の完全一致を必須にする
- Product名を`UIAP Macro Keyboard`、`UIAP Rotary Cursor`、`UIAP Vibration Console`、`UIAP Rotary Haptic`へ固定する
- 03の`make hidcheck`はホスト環境用`doctor`ではなく、独立したデバイス列挙処理を呼び出す
- 各演習READMEに完全な成功出力例を掲載し、受講者へProduct行と最終PASS行の確認を求める

### 根拠

- 誤った演習のファームウェアが書き込まれたデバイスを、操作開始前に発見できる
- 03だけデバイス未接続でも`hidcheck`が成功する状態を解消する
- 受講者が4演習で同じ観点と表示順を使って接続確認できる

### 検証状態

- 4演習の成功出力とProduct不一致失敗を検証する自動テストを追加
- Windows/macOS実機での統一後表示は再確認待ち

---

## 2026-08-11 `04_rotary_cursor_haptic`ホストのWindows/macOS共通化

### 決定

- `host/win/cursor_size_host.py`と`host/mac/cursor_size_host.py`を廃止し、`host/cursor_size_host.py`へ統合する
- `02_rotary_cursor_size`と同じ共通HID・CLI・OSバックエンド構成を使用する
- `04`固有のPID `C005`、入力Report ID 1、触覚Feature Report ID 2、専用状態ファイルを維持する
- OSのカーソル変更と再読取りが成功した時だけ振動を指示する
- 上限／下限、ドライラン、カーソル変更失敗時は振動させない

### 検証状態

- Python構文検査とWindows自己テスト: 合格
- Windows/macOS配布ZIP構成を含む既存テスト11件: 合格
- 同梱Makeによる`host-doctor`と主要ターゲット展開: 合格
- Windows/macOS実機でのカーソル変更・振動・終了時復元: 再確認待ち

---

## 2026-08-11 `03_vibration_motor_console`の必須演習追加

### 決定

- 必須演習を`00`、`01`、`02`、`03`、`04`の5本とする
- `03_vibration_motor_console`は`02_rotary_cursor_size`完了後に行う
- `03`でドライバー回路内蔵5V振動モジュールをVCC→5V、GND→GND、IN→D6/A2 / PC4として追加する
- `03`ではPoC `workspace/poc/vibration_motor_hid`を参考に、Vendor-defined HID Feature ReportでPCから振動モジュールを単体制御する
- 振動レベルは`0`〜`100`とし、`0`はOFF、`1`〜`99`は500Hz PWM、`100`は連続Highとする
- 参加者はPythonを直接実行せず、`make pulse LEVEL=<1..100>`、`make on LEVEL=<1..100>`、`make status`、`make off`を使用する
- 短時間の確認には、自動的にOFFへ戻る`make pulse`を推奨する
- `03`の暫定USB識別子は`1209:C006`、Product `UIAP Vibration Console`、Serial `TEST9-001`とする
- `04_rotary_cursor_haptic`は`03`完了後に行い、振動モジュールが配線済みの状態から開始する
- `04`では振動モジュールの配線を追加・変更しない
- `03`／`04`ともVCC-GND間コンデンサーは追加せず、モーター本体をGPIOへ直接接続しない

### 検証状態

- `motorctl.py`の構文検査、Feature Reportプロトコル自己テスト: 合格
- PWM強度変更後のWindows同梱ツールチェーンによる`03`ビルド: 合格（Flash 2,928 bytes、RAM 212 bytes）
- Windows/macOS配布キットへの5演習収録を含む既存テスト11件: 合格
- `03`の現行PWM強度変更版について、Windows実機での書き込み、USB接続、MakeコマンドによるON/OFFとレベル変更: 利用者実機合格
- `LEVEL=100`は連続Highのソフトウェア上の最大出力とし、Windows向け必須演習として完成扱い
- `03`のmacOS現行演習版の基本動作: Devkit `v0.1.2`で利用者実機合格
- `04`の配線済み開始手順: 実機確認待ち

---

## 2026-08-11 Devkit `v0.1.2`のmacOS演習02・03確認

### 確認結果

- 利用者から、macOS実機で`02_rotary_cursor_size`が正常動作したとの報告を受けた
- 利用者から、同じ環境で`03_vibration_motor_console`が正常動作したとの報告を受けた
- `02`の現行共通Pythonホストと単一ファームウェアをmacOS実機合格とする
- `03`の現行PWM強度変更版、共通Pythonホスト、単一ファームウェアをmacOS実機合格とする
- `02`と`03`はWindows/macOS向けの必須演習として完成扱いとする

### 継続確認

- 詳細ログ、個々のコマンド出力、macOSバージョンは今回記録していない
- `04_rotary_cursor_haptic`のmacOS実機動作は未確認
- `02`のUSB切断時復元、別Mac・別ユーザーでの再現性は未確認

---

## 2026-08-12 PoCの参加者向けDevkit収録

### 決定

- `workspace/poc`の内容をWindows版・macOS版の参加者向けDevkitへ収録する
- PoCは参考・発展用とし、`workspace/exercises`の正式演習とは区別する
- `_template`も新規PoCのひな型として収録する
- 各PoC直下の`win`はWindows版だけ、`mac`はmacOS版だけへ収録する
- ログ、個人状態、通常のビルド生成物など、Devkit全体の除外規則はPoCにも適用する

### 実装状態

- `tools/build_devkit.py`はすでに`workspace`全体を配布対象としており、この方針と一致する
- 配布ZIPの自動テストで、実在するPoCのファームウェアとホストプログラムの収録を確認する

---

## 2026-08-12 当日の生成AI利用・自由制作・配布部品・macOS署名方針

### 決定

- ワークショップ当日のインターネット接続を必須とする
- 参加者は生成AIと相談しながらワークショップを進める
- ワークショップの最終成果物は受講者自身が決め、講師側では一律の制作物を定めない
- 自由制作で使用する部品は、受講者が生成AIと相談し、講師側が用意した部品から選ぶ
- 必須5演習の標準配線は維持するが、その後の自由制作におけるUIAPduinoのピン割り当ては講師側で一元管理しない
- macOS版はDeveloper IDによる署名・公証を行わない
- macOS版は個別許可方式を正式手順として整備し、ブラウザから取得した配布ZIPで検証する
- 現時点で、次の6種類を配布することを決定する
  - センタースイッチ付きロータリーエンコーダーモジュール
  - 振動モジュール
  - アナログジョイスティック
  - RGB LED
  - パッシブブザー
  - タクトスイッチ

### 維持する未決定事項

- 配布部品の型番、参加者1人あたりの数量、予備数、追加部品を含む最終BOM

### 過去決定との関係

- 「ワークショップで最終的に制作するUSBデバイス」は未決定事項ではなく、講師側で決定しない事項へ変更する
- 「参加者が使用する部品の最終構成」と「GPIO割り当ての最終プロファイル」は、全参加者共通の構成を決める対象から外す
- 「ワークショップ当日にインターネット接続を必須にすること」は、本決定により決定済みへ更新する
- 「Developer ID署名・公証または個別許可方式」は、本決定によりDeveloper ID署名・公証を行わず、個別許可方式を採用する
- 生成AIが提案した回路とピン割り当ては自動的に安全確認済みとは扱わず、参加者ごとの制作物について電気的条件と機能競合を確認する

---

## 2026-08-13 受講者の自由制作ディレクトリ

### 決定

- 受講者が作成する完成品は1人あたり最大3件とする
- 自由制作用プログラムの保存先を、1件目から順に次の固定パスとする
  - `workspace/poc/my_device1`
  - `workspace/poc/my_device2`
  - `workspace/poc/my_device3`
- 多くの受講者は1件だけ完成すると想定し、`my_device1`の完成を標準目標とする
- ワークショップ資料、標準コマンド、画面例、生成AI向け共通プロンプトには`my_device1`だけを記載する
- 講師の通常サポートは`my_device1`を対象とする
- `my_device2`と`my_device3`は、`my_device1`を完成させた後、追加のアイデアを自力で試せる受講者が順番に使用する任意枠とする
- `my_device4`以降は作成しない

### 理由

- 初心者が操作するパスと、講師・生成AIが案内するパスを統一する
- 1件目の完成前に複数案へ分散することを防ぐ
- 進行の速い受講者には最大3件まで試行余地を残しながら、標準資料と講師サポートを複雑化させない

### 既存PoCとの関係

- この固定名は受講者の自由制作にだけ適用する
- 主催者用の検証PoCは、従来どおり`workspace/poc/<project-name>`で管理する
- `tools/new_poc.py`の一般PoC作成機能は、この決定だけを理由に廃止しない
