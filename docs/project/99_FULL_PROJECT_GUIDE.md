# XP祭り2026 物理UIワークショップ
# 完全版プロジェクトガイド

更新日: 2026-08-01

この文書は、分割された詳細指示を1つに統合した参照用完全版である。

> `99_FULL_PROJECT_GUIDE.md`は、分割文書から生成する。原則として直接編集せず、各分割文書を更新した後に再生成する。

<!-- Source: 00_PROJECT_OVERVIEW.md -->

# XP祭り2026 物理UIワークショップ
# プロジェクト概要

更新日: 2026-08-01

## 1. 目的

このプロジェクトは、XP祭り2026で実施する「物理UIの電子工作を体験するワークショップ」の企画、調査、設計、開発、検証、および参加者向け資料の作成に使用する。

参加者は、UIAPduino、スイッチ、ロータリーエンコーダー、LED、振動モーターなどを使い、PCとUSB接続する物理UIデバイスの制作を体験する。

本プロジェクトでは、技術的な高度さや構成の美しさより、次を優先する。

- ワークショップ当日に安定して動作する
- 初心者が環境構築で挫折しない
- 講師1人で約8人を支援できる
- 問題発生時に演習を継続しやすい
- WindowsとmacOSの差異を小さくする
- 管理者権限を避け、オンライン取得は固定URL・固定バージョン・SHA-256検証で再現可能にする

## 2. ワークショップ前提

### 運営

- 所要時間は約1.5時間
- 参加者は約8人
- 講師は1人
- 初心者から経験者まで複数レベルが混在する
- ターミナル操作に不慣れな参加者を含む
- UIAPduinoは当日配布する
- 参加者1人につきUIAPduinoを3台配布する計画とする
- はんだ付けは行わない
- ブレッドボードとジャンパー線を使用する
- ブレッドボードはSY-170を複数配布する
- 部品はブレッドボードまたはジャンパー線へ接続できる状態で配布する
- USBケーブルは講師がデータ通信を確認したものを配布する
- USBハブは使用可能とするが、問題発生時はPCへ直結する
- 予備ボードと予備ケーブルを用意する

### 事前準備

- 開発環境は事前配布する
- 参加者はZIPをダウンロードし、完全に展開する
- テキストエディターは参加者が事前に用意する
- VS Code利用者が多い想定だが、特定エディターへ依存しない
- 事前診断を実施できるようにする
- 事前診断結果をフォームで収集できるようにする
- 当日は大規模な環境構築や追加インストールを行わない
- エラー時には診断結果を講師または生成AIへ渡せるようにする

最終参加者向け開発環境もオンライン・ブートストラップ方式とする。初回`setup`や不足物の再取得ではインターネット接続を使用し、取得対象は固定URL、固定バージョン、SHA-256で管理する。ワークショップ当日の運用でどの段階までネットワークを必須とするかは、事前セットアップ運用と合わせて別途確認する。

## 3. 対象ハードウェア

特に指定がない限り、対象ボードは次とする。

- UIAPduino Pro Micro CH32V003 V1.4
- MCU: CH32V003
- PC接続: USB Type-C
- USB: USB 2.0 Low-Speed
- 書き込みUSBと通常のUSB通信は同じコネクターを使用する

回路、ピン配置、電圧、消費電流、USB、タイマー、GPIO、メモリなどを検討するときは、UIAPduino Pro Micro CH32V003 V1.4の仕様を前提とする。

別のボードまたは別バージョンを扱う場合は、その差異を明示する。

### 使用予定部品

入力部品の候補:

- モメンタリスイッチ
- オルタネートスイッチ
- ロータリーエンコーダー
- ロータリーポテンショメーター
- スライドポテンショメーター

出力部品の候補:

- SSD1306 OLED
- コイン型振動モーターモジュール
- WS2812B／NeoPixel

すべてを同時に接続することは前提にしない。参加者が使用する部品の最終構成は未決定である。

## 4. 対象OS

### 正式対応

- Windows 11 x64
- macOS Apple Silicon
- macOSの最低バージョンはmacOS 26

### サポート対象外

- Windows 10
- Windows 11 ARM64
- Intel Mac

主な実験と検証はWindows 11 x64で行う。

参加者向けの開発環境、演習、ソースコード、Makefile、コマンド、手順書は、Windows 11 x64とmacOS Apple Siliconの両方で利用できるように設計する。

Windowsでの成功だけを根拠に、macOSでも確認済みと扱わない。

## 5. 開発環境の基本方針

参加者向け配布物は次の2種類とする。

```text
uiap-devkit-win64.zip
uiap-devkit-macarm64.zip
```

Devkitのバージョンは`MAJOR.MINOR.PATCH`の3桁だけで管理し、`-rc1`、`-testN`などの接尾辞を使用しない。

展開後の最上位ディレクトリ名は次に固定する。

```text
uiap-devkit-win64
uiap-devkit-macarm64
```

起動後、受講者は`cd`コマンドで対象の演習ディレクトリへ移動し、その演習のMakefileターゲットを使用する。主要コマンドは両OSで可能な限り共通化する。

```sh
make
make flash
make clean
make app
make doctor
make report
```

演習フォルダーへの移動を隠す`sample`、`macro`、`blink`などのトップレベルコマンドは使用しない。`cursorapp`、`cursorlist`、`cursorrestore`など特定演習専用のトップレベルコマンドも使用せず、演習ディレクトリ内の`make app`、`make list`、`make restore`へ統一する。

開発環境は、原則として次を満たす。

- 必要なツールと固定済み依存関係は、同梱またはオンライン`setup`の固定取得定義で再現可能にする
- Makefileへ開発者固有の絶対パスを書かない
- 管理者権限を要求しない
- 参加者にZadigやUSBドライバー変更を行わせない
- Python venvのactivate操作を参加者へ要求しない
- ワークショップ中に最新版を取得しない
- 未採用PoC、個人設定、ログ、通常のビルド生成物を配布版へ含めない
- Windows版の展開先は、ローカルドライブ上のASCII・空白なしパスに限定する
- 半角英数字、ドット、ハイフン、アンダースコアだけで構成された複数階層のフォルダーを許可する
- `C:\pj\xpfes2026\uiap-devkit-win64`のような有効な複数階層パスを拒否しない
- 非対応パスだけを`setup`開始前に検出し、推奨移動先を日本語で表示する
- パス判定は共通処理へ集約し、起動、setup、doctorで判定差を発生させない
- `start-uiap`起動後の初期位置は`workspace`とし、受講者自身が`cd`で対象演習へ移動する
- 演習移動・演習固有操作のためのトップレベル別名コマンドを配布しない
- `ch32fun`は固定コミットの完全版から許可リスト方式で参加者向けサブセットを生成する
- 完全な上流ソース、許可リスト、生成スクリプト、ローカルパッチを対応ソースとして別途保持する

### Windows構成の状態

Windows版の標準構成は、MSYS2を使用しないxPackベースのWindowsネイティブ構成とする。

- xPack Windows Build Tools
- xPack GNU RISC-V Embedded GCC
- Windows Command Prompt
- PowerShell補助スクリプト
- 同梱Pythonとhidapi

2026-07-24までにオンライン・ブートストラップ型PoCで、起動、セットアップ、ビルド、USBブートローダー書き込み、USB HID、Pythonホストアプリを確認した。

最終参加者向け版もオンライン・ブートストラップ方式とする。別PC、別ユーザーでの最終版検証は引き続き必要である。過去のMSYS2構成は検証履歴として残すが、現行の参加者向け標準構成には採用しない。

### macOS構成の状態

macOS版は、Apple Silicon arm64ネイティブとし、Rosetta 2、Homebrew、Xcode Command Line Tools、管理者権限を参加者へ要求しない構成を目標とする。

2026-07-31までに、主催者検証版`uiap-devkit-macarm64` `0.2.1-test12`をmacOS 26.5.2のApple Silicon実機で確認した。次は実機確認済みである。

- `start-uiap.command`からの起動
- Apple Silicon arm64ネイティブ動作、Rosetta不使用
- 共通環境変数と初期ディレクトリ`workspace`の設定
- オンライン`setup`
- xPack GNU RISC-V Embedded GCC 14.2.0-3 arm64
- Devkit内GNU Make 4.4.1 arm64
- 固定コミットの`ch32fun`と`rv003usb`
- libusb 1.0.29の静的ビルド
- arm64版`minichlink`のローカル生成、隔離属性処理、アドホック署名、署名検証
- arm64版ネイティブカーソルホストの生成、署名、API自己診断
- `00_onboard_led_blink`のビルド、書き込み、基板上LEDの0.2秒点灯・0.8秒消灯
- `01_macro_keyboard`のビルド、書き込み、HIDキーボード入力
- スイッチ1回で`AbCdE`を入力し、長押しで連続入力せず、再押下、キー解放、USB再接続が正常に動作
- 初回のキーボード設定アシスタントを「終了」で閉じた後も入力でき、再接続時にはアシスタントが再表示されないこと
- `02_rotary_cursor_size`のビルド、書き込み、`1209:C004`のUSB・IOHID列挙
- D8 / PC6、D9 / PC7、GNDへ接続したロータリーエンコーダーのCW／CCW受信
- ネイティブarm64ホストによるカーソルサイズ変更
- `Ctrl+C`終了時の起動前カーソルサイズ復元

macOS版DevkitにはPythonとhidapiを含める。ただし、`02_rotary_cursor_size`の現行ホスト実装自体はPython・hidapiではなくIOKit HIDとネイティブarm64ホストを使用する。カーソルサイズ変更には非公開CoreGraphics APIを使用し、test12ではスカラー引数の`float32`／`float64` ABIを実行時に判定する。macOS 26.5.2の利用者実機では想定動作を確認したが、USB切断時復元、別Mac、別ユーザー、最低対応macOS、将来のmacOS更新後の互換性は未確認である。

最終`ch32fun`許可リスト、`rv003usb`入力SHA-256の正式固定、別Mac・別ユーザー、macOS 26以降での追加検証、署名・公証方針は未確認または未決定である。最終参加者向け版もオンライン初期化型とする。

Windowsの`SystemParametersInfoW`アクション`0x2029`とmacOSの非公開CoreGraphics APIは、互換性リスクを明記し、各リリースで回帰検証することを条件に今回の参加者向けDevkitで使用を許容する。

## 6. ワークショップ必須演習

2026-07-31時点で、次の3演習を必須演習とする。

| 演習 | 目的 | 現在の検証状態 |
|---|---|---|
| `00_onboard_led_blink` | 開発環境、ビルド、書き込み、復旧の基本確認 | Windows、macOSで物理動作確認済み |
| `01_macro_keyboard` | 外付けスイッチとUSB HIDキーボード入力 | Windows、macOSで`AbCdE`入力確認済み |
| `02_rotary_cursor_size` | ロータリーエンコーダーとPC側処理の体験 | Windows、macOSでCW／CCW受信、カーソルサイズ変更、終了時復元を確認済み |

必須演習の決定は、ワークショップで最終的に制作するUSBデバイスや、公開配布用の正式HID Usage、VID:PIDを決定したことを意味しない。

## 7. USBと書き込み

UIAPduino V1.4では、`rv003usb`ベースのUSBブートローダーを使用する。

確認済みブートローダーVID:PID:

```text
1209:B803
```

参加者向け書き込み操作は、原則として次へ統一する。

```sh
make flash
```

書き込み時は、物理USBブートローダーが1台だけであることを確認する。

Windowsでは、1台の物理USBデバイスが親USBデバイスと複数のHID子デバイスとして表示される場合がある。物理ボード数は、現在接続中のUSB親デバイス単位で判定する。

USBブートローダーが壊れた場合、ワークショップ中は予備UIAPduinoへ交換する。SWIOによる復旧は講師の事後作業とする。

## 8. 検証済みPoC

2026-07-26までに、Windows 11 x64で次を確認した。

- WindowsネイティブDevkitの起動と再起動後の再現
- 基板上LED点滅
- `make clean`、`make`、`make flash`
- D5へ接続したモメンタリスイッチによるHIDキーボード入力
- スイッチ押下1回による`AbCdE`入力
- D8、D9、GNDへ接続した3端子ロータリーエンコーダー
- Vendor-defined HIDによる回転情報送信
- PythonとhidapiによるHID情報受信
- Windowsのポインターサイズ変更
- Vendor-defined HID Feature Reportによる振動モーター制御
- `workspace/exercises/03_pot_cursor_haptic` v1.0.8のビルド、書き込み、HID列挙
- RV09 B10Kポテンショメーターの値を0～1023として取得
- ポテンショメーター値に応じたWindowsポインターサイズ15段階変更
- サイズ変更成功時の振動モーターモジュールによるクリック感
- 振動レベル4（80msを2回、間隔40ms）の知覚性
- ADC安定化による境界付近のポインターサイズふらつき抑制

`00_onboard_led_blink`、`01_macro_keyboard`、`02_rotary_cursor_size`は必須演習として採用済みである。振動モーター、ポテンショメーター、OLED、ブザーなど、その他のPoCは必須演習または最終制作物としての採用を意味しない。

2026-07-31までに、macOS 26.5.2のApple Silicon実機で次を確認した。

- `uiap-devkit-macarm64` `0.2.1-test12`の起動とオンライン初期化
- arm64ネイティブ、Rosetta不使用
- GNU Make 4.4.1とxPack RISC-V GCC 14.2.0-3
- 固定コミットの`ch32fun`、`rv003usb`
- libusb 1.0.29とarm64版`minichlink`の主催者ローカルビルド
- `00_onboard_led_blink`のビルド、書き込み、基板上LEDの物理点滅
- `01_macro_keyboard`のHID入力、`AbCdE`、長押し抑止、再押下、キー解放、USB再接続
- 初回キーボード設定アシスタントを「終了」で閉じる手順
- `02_rotary_cursor_size`のUSB・IOHID列挙、CW／CCW入力
- `02_rotary_cursor_size`のカーソルサイズ変更と`Ctrl+C`終了時復元

`02_rotary_cursor_size`はmacOS 26.5.2のApple Silicon実機で基本動作を確認した。非公開CoreGraphics APIの使用は今回の参加者向けDevkitで許容するが、USB切断時復元、別Mac・別ユーザー、macOS 26以降での追加確認、将来互換性は引き続き回帰検証対象とする。

詳細は`70_VALIDATION_RESULTS.md`を参照する。

## 9. 未決定事項

次は、明示的に決定されるまで未決定として扱う。

- ワークショップで最終的に制作するUSBデバイス
- 最終的に使用するHID Usage
- USBメディアコントローラーの採用
- 振動モーターコントローラーの採用
- ポテンショメーター＋振動フィードバック演習の参加者向け採用
- Windows版の正式ランタイム構成
- アプリケーション用の正式VID:PID
- USBシリアル番号の生成方式
- 参加者が使用する部品の最終構成
- GPIO割り当ての最終プロファイル
- macOS版の最終ランタイム構成、オフライン化、`02_rotary_cursor_size`の公開APIだけで実現できる代替方式
- HID経由の自動ブートローダー移行
- 複数UIAPduinoを使用する最終演習構成

PoCで使用した次の値は一時値であり、正式仕様として扱わない。

```text
1209:C003
1209:C004
1209:D003
TEST3-001
TEST7-001
```

## 10. 基本方針と優先順位

複数案がある場合は、次の順序で評価する。

1. ワークショップ当日に安定して動作する
2. WindowsとmacOSの差異が小さい
3. 初心者が理解しやすい
4. セットアップ手順が短い
5. トラブル発生時に復旧しやすい
6. 管理者権限を必要としない
7. インターネット接続を必要としない
8. 部品点数と追加費用が少ない
9. 技術的に高度である

高度だが不安定な方法より、単純で再現性の高い方法を優先する。

問題解決に時間がかかる場合は、予備ボード、既知の正常な演習、配線済み見本、完成済みデモへ切り替え、演習継続を優先する。

## 11. 決定事項と検証状態

過去の会話、調査、PoCで候補として挙げられた内容を、明示的な決定なしに採用しない。

回答と文書では、必要に応じて次を区別する。

- 決定済み
- 検討中
- 候補
- 未確認
- 却下または未採用
- PoC限定

技術項目は、少なくとも次の状態を区別して記録する。

- 提案
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

最新の決定内容は`90_DECISIONS.md`、実機検証結果は`70_VALIDATION_RESULTS.md`を参照する。

## 12. 文書の参照順序

関連する作業を行うときは、次の順序で参照する。

1. `90_DECISIONS.md`
2. 作業分野に対応する詳細文書
3. `70_VALIDATION_RESULTS.md`
4. `99_FULL_PROJECT_GUIDE.md`

詳細文書の役割:

| ファイル | 内容 |
|---|---|
| `00_PROJECT_OVERVIEW.md` | 目的、対象、前提、優先順位 |
| `10_DEVKIT_STRUCTURE.md` | 配布パッケージとディレクトリ構成 |
| `15_CH32FUN_SUBSET_RULES.md` | ch32fun参加者向けサブセットの許可リスト、来歴、検証 |
| `20_BUILD_RULES.md` | Makefile、パス、改行、依存関係 |
| `30_HARDWARE_RULES.md` | 回路、GPIO、電源、USB、安全性 |
| `40_WORKSHOP_GUIDE_RULES.md` | 参加者向け手順書の記述規約 |
| `50_RELEASE_CHECKLIST.md` | ZIP作成、不要物除外、リリース検証 |
| `60_TROUBLESHOOTING.md` | 問題の切り分けと復旧方針 |
| `70_VALIDATION_RESULTS.md` | 実機検証結果、確認済み範囲、未確認事項 |
| `90_DECISIONS.md` | 決定事項、検討中、移行状況 |
| `99_FULL_PROJECT_GUIDE.md` | 分割文書を統合した参照用完全版 |

`99_FULL_PROJECT_GUIDE.md`は、分割文書を更新した後に再生成する。

## 13. 2026-08-01 Windowsオンライン初期化型Devkitのダウンロード表示

Windows版の最終参加者向け配布もオンライン初期化型とする。xPack GNU RISC-V Embedded GCCなどの大容量アーカイブ取得中に状態を確認できるようにし、取得対象は固定ロックとSHA-256で管理する。

標準方式:

- Windows標準の`curl.exe`をPowerShell補助スクリプトから明示的に実行する
- 進捗バーと完了割合をcurlの進捗表示で確認可能にする
- `.part`、再試行、条件付き再開、SHA-256検証、キャッシュ再利用を共通処理へ集約する
- ダウンロードURL、SHA-256、展開先、コンポーネント種別を固定ロックファイルへ記録する
- ダウンロード処理の失敗を、展開、インストール、ビルドの失敗と区別する

`uiap-devkit-win64` `0.5.2-test15`は、この方式にPowerShell文字コード修正とWindows起動シェル絶対パス化を加えた主催者検証版である。2026-08-01時点ではtest15のパッケージ静的検査までで、Windows 11 x64実機確認済みとは扱わない。

## 14. 2026-08-01 Windows起動シェルの解決規則

Windows版Devkitは、専用Command PromptおよびWindows PowerShellをPATH検索だけに依存して起動しない。

- Command Prompt: `%SystemRoot%\System32\cmd.exe`
- Windows PowerShell 5.1: `%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe`
- Devkit用PATHへSystem32、Wbem、Windows PowerShellを明示的に保持する
- 起動シェルが存在しない場合は、ウィンドウを即時終了せずエラーコードと実体パスを表示する

`0.5.1-test14`では相対名`cmd.exe`の解決失敗を利用者実機で確認した。`0.5.2-test15`で修正し、実機再確認待ちとする。

<!-- Source: 10_DEVKIT_STRUCTURE.md -->

# 開発環境とディレクトリ構成

更新日: 2026-08-01

## 1. この文書の目的

この文書は、XP祭り2026で使用するUIAP Devkitのパッケージ名、ディレクトリ構成、各領域の責務、およびWindowsとmacOSの差異を定める。

対象:

- Windows 11 x64
- macOS Apple Silicon
- UIAPduino Pro Micro CH32V003 V1.4

最新の正式決定は`90_DECISIONS.md`、ビルド規約は`20_BUILD_RULES.md`、実機検証結果は`70_VALIDATION_RESULTS.md`を参照する。

## 2. Windows版の現行決定

Windows版ではMSYS2を使用しない。

標準構成は、Windowsネイティブ環境とする。

- xPack Windows Build Tools
- xPack GNU RISC-V Embedded GCC
- Windows Command Prompt
- PowerShell補助スクリプト
- 同梱Python
- hidapi
- `ch32fun`
- `rv003usb`
- `minichlink`

参加者は、トップレベルの`start-uiap.cmd`から環境を起動する。

参加者に、MSYS2、UCRT64、MinGW、Cygwin、WSL、システムPython、Homebrew相当の外部環境を選択させない。

この決定により、次はWindows版の標準構成へ含めない。

```text
runtime/msys64
msys2.exe
ucrt64.exe
mingw64.exe
clang64.exe
```

## 3. 配布パッケージ名

参加者へ事前配布する開発環境は次の2種類とする。

- Windows 11 x64版: `uiap-devkit-win64.zip`
- macOS Apple Silicon版: `uiap-devkit-macarm64.zip`

展開後の最上位ディレクトリ名は次に固定する。

```text
uiap-devkit-win64
uiap-devkit-macarm64
```

バージョン番号を配布ファイル名へ追加する場合:

```text
uiap-devkit-win64-<version>.zip
uiap-devkit-macarm64-<version>.zip
```

展開後のディレクトリ名には、原則としてバージョン番号を含めない。

バージョン文字列は`MAJOR.MINOR.PATCH`の3桁だけを使用する。`-rc1`、`-testN`などの接尾辞は使用しない。

検証用ZIPと最終参加者向けZIPを区別する。

最終参加者向け版もオンライン・ブートストラップ方式とする。`setup`で取得する入力は固定URL、固定バージョン、SHA-256で管理する。

## 4. Windows版の現行ディレクトリ構成

2026-07-25時点で確認したWindows版のディレクトリ構成は次のとおり。

`tree`コマンドではファイルが表示されないため、トップレベルの`README.md`、`VERSION`、`manifest.sha256`、`start-uiap.cmd`などは別途管理対象とする。

```text
uiap-devkit-win64/
├── README.md
├── VERSION
├── manifest.sha256
├── start-uiap.cmd
├── .state/
├── docs/
├── firmware/
├── licenses/
├── logs/
├── runtime/
│   ├── build-tools/
│   ├── downloads/
│   ├── python/
│   └── toolchain/
├── scripts/
│   ├── cmd/
│   └── python/
└── workspace/
    ├── deps/
    │   ├── ch32fun/
    │   └── rv003usb/
    └── exercises/
        ├── 00_onboard_led_blink/
        ├── 01_macro_keyboard/
        ├── 02_rotary_cursor_size/
        │   └── host/
        └── 03_pot_cursor_haptic/
            ├── docs/
            └── host/
```

この構成をWindows版の標準とする。

PC側ホストプログラムは、対応する演習の`host`ディレクトリへ配置する。トップレベルの`workspace/host`は作成しない。PC側プログラムを使用しない演習には、空の`host`ディレクトリを作成しない。

`workspace/poc`は主催者用開発環境では使用できるが、現在の参加者向けツリーには存在しない。未採用PoCを参加者向け配布版へ追加しない。

## 5. トップレベル項目の責務

| 項目 | 用途 |
|---|---|
| `README.md` | 参加者が最初に読む起動・診断・演習案内 |
| `VERSION` | Devkit名、バージョン、Platform、Build-Date、配布方式 |
| `manifest.sha256` | 配布内容の完全性確認 |
| `start-uiap.cmd` | Windowsネイティブ開発コンソールの起動 |
| `runtime` | Make、シェル互換ツール、RISC-V GCC、Pythonなど |
| `scripts` | セットアップ、診断、書き込み、HID確認、復旧 |
| `workspace` | 固定依存、参加者向け演習、および各演習内のホスト側ソース |
| `docs` | セットアップ、演習、配線、既知問題 |
| `firmware` | ブートローダー、復旧用などの配布済みバイナリ |
| `licenses` | ライセンス、第三者通知、対応ソース情報 |
| `logs` | ホストアプリと診断処理の実行ログ |
| `.state` | セットアップ状態やOS設定復元情報などの内部状態 |

## 6. `runtime`

`runtime`には、参加者が直接編集しないWindowsネイティブ実行環境を格納する。

```text
runtime/
├── build-tools/
├── downloads/
├── python/
└── toolchain/
```

### 6.1 `runtime/build-tools`

xPack Windows Build Toolsを格納する。

現行ツリーでは、少なくとも次を含む。

```text
runtime/build-tools/
├── bin/
├── distro-info/
│   └── licenses/
├── include/
└── share/
```

用途:

- GNU Make
- BusyBox for Windowsなどの補助コマンド
- ビルド時に必要なPOSIX互換処理
- 同梱物のライセンス情報

参加者は`runtime/build-tools/bin`内のコマンドを直接実行しない。`start-uiap.cmd`とMakefileがPATHを設定する。

### 6.2 `runtime/toolchain`

xPack GNU RISC-V Embedded GCCを格納する。

現行ツリーでは、少なくとも次を含む。

```text
runtime/toolchain/
├── bin/
├── distro-info/
│   └── licenses/
├── include/
├── lib/
├── libexec/
├── riscv-none-elf/
└── share/
```

主なコマンド:

```text
riscv-none-elf-gcc
riscv-none-elf-objcopy
riscv-none-elf-size
```

ツールチェーン内部には、多数のRISC-V ISA、ABI、GCC内部ファイル、Newlib、GDB、Binutils、ライセンスファイルが含まれる。

内部ディレクトリを手作業で削除しない。

サイズ削減を行う場合は、必要なターゲット、ライブラリ、ライセンス、再現手順を確認し、自動化されたサブセット生成手順として管理する。

### 6.3 `runtime/python`

Windows x64用の同梱Pythonとhidapiを格納する。

```text
runtime/python/
└── Lib/
    └── site-packages/
        └── hidapi-0.15.0.dist-info/
            └── licenses/
```

実際には、Python実行ファイル、標準ライブラリ、hidapiの拡張モジュールも同じPythonランタイム内へ配置する。

参加者に次を要求しない。

- システムPythonのインストール
- `pip install`
- venvのactivate
- PATHへのPython追加
- 管理者権限

Pythonの診断処理は、複雑な`python -c`ではなく、`scripts/python`内の`.py`ファイルとして実行する。

### 6.4 `runtime/downloads`

オンライン・ブートストラップ方式の`setup`が取得したアーカイブやチェックサムを格納する。

用途:

- セットアップの再実行
- ダウンロード失敗からの復旧
- SHA-256検証
- 取得元の再現性確認

`runtime/downloads`は最終参加者向け版でもダウンロードキャッシュとして使用してよい。配布ZIPの初期状態には、原則として取得済みアーカイブを含めない。

配布ZIPの初期状態では、原則として次を除外する。

- 取得済みZIPやtarball
- 一時ダウンロードファイル
- 展開前アーカイブ
- 不要なSHA sidecar
- セットアップ失敗時の残骸

`setup`完了後は、取得・展開したランタイムを`build-tools`、`toolchain`、`python`などの所定位置へ配置する。

## 7. `scripts`

Windowsネイティブ構成では、参加者向けコマンドラッパーとPython補助処理を分離する。

```text
scripts/
├── cmd/
└── python/
```

### 7.1 `scripts/cmd`

Windows Command Promptから使用する、Devkit全体に共通する参加者向けコマンドだけを格納する。

標準例:

```text
setup
doctor
versions
report
```

実装例:

```text
scripts/cmd/
├── setup.cmd
├── doctor.cmd
├── versions.cmd
├── report.cmd
└── welcome.cmd    # 起動時表示用の内部補助
```

演習ディレクトリへの移動や、特定演習だけのホストアプリ操作をトップレベルコマンドへしない。次の名前は参加者向け標準コマンドとして配布しない。

```text
sample
macro
blink
hidcheck
cursorapp
cursorlist
cursorrestore
cursorstore
```

受講者は`cd`で`workspace/exercises/<exercise-name>`へ移動し、その演習のMakefileターゲットを使用する。

```text
make
make flash
make hidcheck
make app
make list
make restore
```

この方針により、実行対象の演習ディレクトリがコマンド行と現在位置から明確になり、グローバル別名と演習Makefileの機能重複を避ける。

### 7.2 `scripts/python`

Pythonによる診断、HID確認、OS設定復元などの共通処理を格納する。

例:

```text
scripts/python/
├── hidapi_probe.py
└── ...
```

PowerShell、Command Prompt、Pythonの引用符解釈をまたぐ複雑なワンライナーを使用しない。

### 7.3 スクリプト共通規則

- 自身の配置場所からDevkitルートを解決する
- カレントディレクトリへ依存しない
- 固定ドライブ文字を使用しない
- 固定ユーザー名を使用しない
- 終了コードを呼び出し元へ伝搬する
- 同じ原因に同じエラーコードを使用する
- 個人情報や不要なUSB識別子をログへ出力しない
- 参加者にPowerShellスクリプト名や内部引数を入力させない

### 7.4 演習ディレクトリへの移動

`start-uiap.cmd`は`workspace`を初期ディレクトリとする。受講者は対象演習を確認し、自分で`cd`を実行する。

Windows Command Promptの例:

```text
cd /d "%UIAP_WORKSPACE%\exercises\00_onboard_led_blink"
cd /d "%UIAP_WORKSPACE%\exercises\01_macro_keyboard"
cd /d "%UIAP_WORKSPACE%\exercises\02_rotary_cursor_size"
cd /d "%UIAP_WORKSPACE%\exercises\03_pot_cursor_haptic"
```

macOSの例:

```sh
cd "$UIAP_WORKSPACE/exercises/00_onboard_led_blink"
cd "$UIAP_WORKSPACE/exercises/01_macro_keyboard"
cd "$UIAP_WORKSPACE/exercises/02_rotary_cursor_size"
cd "$UIAP_WORKSPACE/exercises/03_pot_cursor_haptic"
```

手順書では、対象演習ごとに実行する`cd`を明記する。参加者に演習番号や別名コマンドを暗記させない。

## 8. `workspace`

標準構成:

```text
workspace/
├── deps/
└── exercises/
    └── <exercise-name>/
        └── host/    # PC側プログラムがある演習だけ
```

`workspace/host`は使用しない。ホストプログラムを演習と同じ単位で配布、検証、削除できる構成とする。

### 8.1 `workspace/deps`

固定済みの外部依存関係を格納する。

```text
workspace/deps/
├── ch32fun/
└── rv003usb/
```

参加者向け`workspace/deps/ch32fun`は、固定済み上流コミットの完全版ではなく、許可リスト方式で生成したサブセットとする。

概念上、次を含む。

```text
workspace/deps/ch32fun/
├── LICENSE
├── README.md
├── SUBSET.md
├── UPSTREAM_COMMIT
├── ALLOWLIST.txt
├── ch32fun/
├── minichlink/
├── misc/
└── extralibs/
```

実際の配布対象はディレクトリ単位ではなく、リリース元の許可リストへ記載した相対ファイルパス単位で決定する。

原則として次は参加者向けサブセットへ含めない。

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

完全な固定コミットの上流ソース、許可リスト、生成スクリプト、ローカルパッチ、再生成手順は対応ソースアーカイブとして別途保持する。詳細は`15_CH32FUN_SUBSET_RULES.md`を参照する。

`rv003usb`には、少なくとも次が含まれる。

- `rv003usb`
- `lib`
- `bootloader`
- `demo_hidapi`
- `demo_composite_hid`
- `serial_number_utility`
- 各種demoおよびtesting

外部依存は、検証済みコミットへ固定する。

`workspace/deps/VERSIONS.md`を追加し、次を記録することを推奨する。

- 配布元
- コミットIDまたはバージョン
- 取得日
- SHA-256
- ライセンス
- ローカル変更
- 動作確認OS

`.git`を参加者向けZIPへ含めない場合でも、コミットIDを記録する。

`ch32fun`のサブセットには、上流コミット、入力SHA-256、サブセット生成規則、ローカルパッチ、サブセットであることを追加記録する。

`rv003usb`など他の依存関係をサブセット化する場合も、同じ許可リスト、来歴、ライセンス、再生成、検証の原則を適用する。

### 8.2 `workspace/exercises`

参加者向けまたは実機検証用の演習を格納する。

現行構成:

```text
workspace/exercises/
├── 00_onboard_led_blink/
├── 01_macro_keyboard/
├── 02_rotary_cursor_size/
└── 03_pot_cursor_haptic/
```

役割:

| 演習 | 内容 |
|---|---|
| `00_onboard_led_blink` | 必須。基板上LEDとビルド・書き込み確認 |
| `01_macro_keyboard` | 必須。D5スイッチによるUSB HIDキーボード |
| `02_rotary_cursor_size` | 必須。D8/D9エンコーダーとOS別ホストアプリ |
| `03_pot_cursor_haptic` | PoC。RV09ポテンショメーター、Windowsポインターサイズ、振動フィードバック |

`00_onboard_led_blink`、`01_macro_keyboard`、`02_rotary_cursor_size`はワークショップ必須演習として採用済みである。`03_pot_cursor_haptic`はWindows実機PoCで、v1.0.8の統合動作とADC安定化を確認済みだが、必須演習には採用していない。

各演習は、原則として次を含む。

```text
<exercise>/
├── README.md
├── Makefile
├── .gitignore
├── <main-source>.c
├── funconfig.h
├── usb_config.h
└── host/                  # PC側プログラムがある場合だけ
    ├── README.md
    └── <host-program>.py
```

USBを使用しない演習では`usb_config.h`を省略してよい。PC側プログラムを使用しない演習では`host`を省略する。

`03_pot_cursor_haptic`の確認済み構成:

```text
workspace/exercises/03_pot_cursor_haptic/
├── README.md
├── Makefile
├── pot_cursor_haptic.c
├── funconfig.h
├── usb_config.h
├── docs/
│   ├── VALIDATION.md
│   └── WIRING.md
└── host/
    ├── pot_cursor_host.py
    ├── hidcheck.py
    ├── haptic_test.py
    ├── cursor_test.py
    ├── restore_cursor.py
    └── 補助モジュール
```

この演習はWindows 11 x64向けPoCであり、参加者向け必須演習としての採用は未決定である。

### 8.3 各演習の`host`

PC側ホストプログラムは、対応する演習ディレクトリの直下にある`host`へ格納する。

ロータリーエンコーダー演習の例:

```text
workspace/exercises/02_rotary_cursor_size/
├── README.md
├── Makefile
├── rotary_cursor_size.c
├── funconfig.h
├── usb_config.h
└── host/
    ├── README.md
    ├── cursor_size_host.py       # Windows版
    └── cursor_size_host.c        # macOS Apple Silicon版
```

規則:

- `workspace/host`へ共通配置しない
- PC側プログラムがない演習に空の`host`を作成しない
- `make app`は現在の演習内にある`host`を参照する
- 演習間で別演習の`host`を直接参照しない
- Devkit全体で使用する診断コードは`scripts/python`へ配置する
- Pythonホストアプリは`runtime/python`を使用し、システムPythonへ依存しない
- macOS版DevkitにもPython・hidapiを含める。ただし`02_rotary_cursor_size`の現行ホストはネイティブarm64 CLIであり、当該演習の実行自体はPython・hidapiへ依存しない
- OS固有コードが必要な場合も、当該演習の`host`配下で共通処理と分離する

### 8.4 `workspace/poc`

現行の参加者向けツリーには存在しない。

主催者用の未採用PoCを保持する場合は、内部開発版だけに次を追加してよい。

```text
workspace/poc/
```

参加者向けZIPへ未採用PoCを含めない。

PoCを演習へ採用するときは、次を行う。

1. `workspace/exercises`へ移す
2. 固定パスを除去する
3. 参加者向けREADMEを作成する
4. WindowsとmacOSで検証する
5. `70_VALIDATION_RESULTS.md`へ記録する
6. `90_DECISIONS.md`へ採用決定を記録する

## 9. `docs`

参加者向け文書を格納する。

推奨構成:

```text
docs/
├── setup-windows11.md
├── setup-macos.md
├── workshop-guide.md
├── troubleshooting.md
├── validation-scope.md
├── wiring/
└── images/
```

用途:

- Windows固有の起動と診断
- macOS固有の起動、権限、Gatekeeper
- 共通演習手順
- 参加者向けの簡略復旧手順
- 当該Devkit版の確認済み範囲
- 部品型番ごとの配線資料
- 個人情報を除去した図とスクリーンショット

プロジェクト管理用の詳細文書を、そのまま参加者向けZIPへ入れる必要はない。

## 10. `firmware`

復旧用、初期化用、ブートローダーなど、配布理由が明確なバイナリを格納する。

```text
firmware/
├── bootloader/
├── recovery/
└── README.md
```

参加者向け`firmware`へ含める範囲は、通常使用するものと、講師が当日に行う簡易復旧に必要なものへ限定する。SWIOなど専用機材を使う深い復旧用資材は、参加者向けDevkitとは分離して管理してよい。

各バイナリに次を記録する。

- 対象ボード
- ボードバージョン
- ビルド元ソース
- ビルド条件
- バージョン
- SHA-256
- 使用目的
- 書き込み方法
- 参加者用または講師専用

通常の演習ビルド生成物を格納しない。

## 11. `licenses`

同梱コンポーネントのライセンスと対応ソース情報を格納する。

推奨構成:

```text
licenses/
├── COMPONENTS.csv
├── THIRD_PARTY_NOTICES.md
├── SOURCE-OFFER.md
├── sbom/
└── texts/
```

現行のxPackランタイムは、各配布物内部の`distro-info/licenses`にもライセンス情報を含む。

トップレベル`licenses`では、参加者が確認しやすい形で全同梱物を横断的に整理する。

## 12. `logs`

ホストアプリ、診断、書き込み補助処理のログを格納する。

例:

```text
logs/
├── README.md
├── cursor-YYYYMMDD-HHMMSS.log
└── report-YYYYMMDD-HHMMSS.txt
```

ログへ含めてよいもの:

- Devkitバージョン
- OSとアーキテクチャ
- 対象演習
- VID:PID
- 製品名
- Usage PageとUsage
- 接続と切断
- 最初のエラー
- OS設定復元結果

ログへ含めないもの:

- 不要なユーザー名
- ホームディレクトリ
- 個人情報
- 無関係なUSBデバイスのシリアル番号
- MCU UUID

生成済みログをリリースZIPへ含めない。

## 13. `.state`

参加者が直接編集しない内部状態を格納する。

用途:

- セットアップ完了状態
- 取得済み依存の検証結果
- ホストアプリ起動前のOS設定値
- 設定復元用情報
- 内部マイグレーション状態

規則:

- 個人情報を保存しない
- 別PCへコピーして利用する前提にしない
- 削除しても再生成できる
- 壊れた場合の初期化手順を用意する
- 利用者の実行後状態をリリースZIPへ含めない

## 14. 共通環境変数

必須:

```text
UIAP_DEVKIT_ROOT
UIAP_WORKSPACE
```

必要に応じて使用:

```text
UIAP_RUNTIME
UIAP_TOOLCHAIN_BIN
UIAP_FIRMWARE
UIAP_PYTHON
```

Windowsの想定:

```text
UIAP_RUNTIME=%UIAP_DEVKIT_ROOT%\runtime
UIAP_TOOLCHAIN_BIN=%UIAP_RUNTIME%\toolchain\bin
UIAP_PYTHON=%UIAP_RUNTIME%\python\python.exe
UIAP_FIRMWARE=%UIAP_DEVKIT_ROOT%\firmware
```

Windows上の環境変数はバックスラッシュ形式でもよい。

MakefileからPOSIX互換シェルへ渡す場合は、`20_BUILD_RULES.md`に従って`C:/...`形式へ正規化する。

Makefileやソースコードに、ドライブ文字、ユーザー名、ホームディレクトリ、展開先を固定しない。

## 15. `start-uiap.cmd`

Windows版のトップレベル起動ファイルは、少なくとも次を行う。

1. `%~dp0`で自身のディレクトリを取得
2. `UIAP_DEVKIT_ROOT`を設定
3. `UIAP_WORKSPACE`を設定
4. `runtime/build-tools/bin`をPATHへ追加
5. `runtime/toolchain/bin`をPATHへ追加
6. `runtime/python`を必要に応じて参照可能にする
7. `scripts/cmd`をPATHへ追加し、Devkit共通コマンドだけを利用可能にする
8. 初期ディレクトリを`workspace`へ設定
9. Devkitバージョンを表示
10. セットアップ状態を表示
11. `cd`による演習移動例と、演習内で使用する`make`ターゲットを表示
12. `sample`、`macro`、`cursorapp`などの演習固有別名を表示しない
13. Windows Command Promptを開始

MSYS2シェルを起動しない。

参加者へランタイムの選択を要求しない。

固定パスを使用しない。

禁止例:

```text
C:\pj\xpfes2026\uiap-devkit-win64
C:\Users\<user>
```

## 16. オンライン・ブートストラップ方式

### 16.1 検証版と最終版の共通方式

目的:

- ツール選定
- 配布元URLとSHA-256の確認
- セットアップ処理の検証
- 構成変更の反復

許容:

- `setup`によるオンライン取得
- `runtime/downloads`
- 取得済みファイルの再利用
- 詳細ログ
- 検証用エラーコード

検証版と最終版は同じオンライン取得方式を使用し、最終版では取得元、バージョン、SHA-256、再試行、キャッシュ再利用をリリース条件として固定する。

### 16.2 最終参加者向け版

次を満たす。

- 初回`setup`はオンラインで固定済み入力を取得する
- `runtime/python`とhidapiをWindows・macOSの両方へ導入する
- `workspace/deps`は現行の固定・サブセット方式を維持する
- 取得URL、保存ファイル名、アーカイブ形式、SHA-256を固定する
- ダウンロード失敗、SHA-256不一致、途中再実行、キャッシュ再利用を検証する
- 管理者権限不要
- 実行ログと利用者の`.state`を配布ZIPから除外する
- 未採用PoCを除外する
- ライセンスと対応ソース情報を管理する

## 17. 参加者向けZIPから除外するもの

- `runtime/downloads`内の不要なアーカイブ
- セットアップ途中の一時ファイル
- 実行ログ
- 利用者固有の`.state`
- 未採用PoC
- 不要な`.git`
- 個人設定
- パケットキャプチャ
- 開発者固有の絶対パス
- MCU UUID
- バックアップファイル
- OS生成ファイル
- Windows予約名
- 通常のビルド生成物

通常の生成物:

```text
*.bin
*.elf
*.hex
*.lst
*.map
*_ext.bin
firmware.bin
```

復旧用として必要なバイナリは`firmware`へ移し、出所とSHA-256を記録する。

## 18. macOS版との対応

macOS版もMSYS2を使用しない。Apple Silicon arm64ネイティブのランタイムを使用する。

2026-07-29時点の主催者検証版`0.1.7-test8`は、オンライン初期化型として次の構成を使用する。

```text
uiap-devkit-macarm64/
├── README.md
├── START-HERE.txt
├── VERSION
├── manifest.sha256
├── bootstrap.lock
├── start-uiap.command
├── .state/
├── docs/
├── firmware/
├── licenses/
├── logs/
├── runtime/
│   ├── bin/
│   │   ├── make
│   │   ├── minichlink
│   │   └── minichlink.build-info
│   ├── build-tools/
│   │   └── bin/gmake
│   ├── build/          # 主催者ビルド用。参加者向けZIPから除外
│   ├── downloads/      # オンライン検証キャッシュ。最終構成を別途決定
│   ├── lib/
│   ├── python/         # test8では未実装
│   ├── share/
│   └── toolchain/
├── scripts/
│   ├── bin/
│   │   ├── setup
│   │   ├── build-minichlink
│   │   ├── doctor
│   │   ├── versions
│   │   └── report
│   ├── lib/
│   ├── python/
│   └── zsh/
└── workspace/
    ├── deps/
    │   ├── ch32fun/
    │   └── rv003usb/
    └── exercises/
        └── 00_onboard_led_blink/
```

`start-uiap.command`は自身の配置ディレクトリからDevkitルートを決定し、初期ディレクトリを`workspace`とする。読み込まれるスクリプトが呼び出し元の`$0`だけを基準にルートを決めないようにする。

### 18.1 参加者向け最終版の要件

参加者向け最終版では次を必須にしない。

- Rosetta 2
- Homebrewのインストール
- Xcode Command Line Tools
- 管理者権限
- システムの`/usr/bin/make`
- システムPython
- HomebrewやXcode Command Line Toolsなど、Devkit外の追加インストール

GNU MakeはDevkit内の`runtime/build-tools/bin/gmake`を使用し、参加者向けコマンド名は`make`のままとする。取得元がHomebrewボトルであっても、参加者にHomebrew本体をインストールさせない。

### 18.2 主催者用`build-minichlink`

`build-minichlink`は主催者専用の配布準備・検証コマンドであり、参加者向け通常手順へ含めない。

主催者用ビルドでは次を使用する。

- Xcode Command Line ToolsのApple clangとmacOS SDK
- 固定コミットの`ch32fun`に含まれる`minichlink`ソース
- libusb 1.0.29
- Devkit内GNU Make

生成物は`runtime/bin/minichlink`へ配置し、次を実施する。

1. Mach-O arm64検査
2. 動的依存検査
3. `/opt/homebrew`、`/usr/local`、開発者ホーム配下の依存拒否
4. `minichlink`単体の`com.apple.quarantine`除去
5. アドホック署名
6. `codesign --verify`
7. 隔離属性残存検査
8. SHA-256とビルド来歴記録

Devkit全体へ再帰的な隔離属性削除を行わない。`runtime/build`とオンライン取得キャッシュは、参加者向け最終ZIPへそのまま含めない。

### 18.3 2026-07-29実機確認済み

- macOS 26.5.2、Apple Silicon arm64
- Rosetta変換なし
- `start-uiap.command`起動
- Devkitルートと`workspace`のパス解決
- オンライン`setup`
- xPack GNU RISC-V Embedded GCC 14.2.0-3
- GNU Make 4.4.1 arm64
- 固定コミットの`ch32fun`と`rv003usb`
- libusb 1.0.29静的ライブラリのビルド
- arm64版`minichlink`のローカル生成
- `minichlink`の隔離属性なし、アドホック署名検証成功
- `doctor`で`PASS=32 WARN=1 FAIL=1`
- `00_onboard_led_blink`のビルド
- FLASH 444 B、RAM 0 B
- USBブートローダー`1209:B803`とCH32V003の検出
- `make flash`、`Image written.`、`Booting`
- 基板上LEDの0.2秒点灯・0.8秒消灯

### 18.4 未確認・リリース阻害項目

- Devkit内Pythonとhidapi
- HIDホストアプリ
- 最終許可リスト版`ch32fun`
- 入力アーカイブSHA-256の正式固定
- `-I/usr/include/newlib`への暗黙依存除去
- 最終オンライン`setup`の通し検証
- Developer ID署名・公証または正式な個別許可方針
- 別のApple Silicon Mac、別ユーザー、macOS 26以降の対象環境
- 最終オンライン・ブートストラップ版の通し検証

未署名・未公証の検証版では、ブラウザから取得したZIPの初回起動時にGatekeeperの個別許可が必要になる。Gatekeeper全体の無効化やDevkit全体への無差別な隔離属性削除を標準手順にしない。

## 19. 推奨展開先

Windows:

```text
C:\uiap\uiap-devkit-win64
```

または:

```text
C:\pj\uiap-devkit-win64
```

macOS:

```text
~/uiap/uiap-devkit-macarm64
```

標準展開先では次を避ける。

- 空白
- 日本語
- 極端に長いパス
- 同期対象ディレクトリ
- 管理者権限が必要な場所
- ZIP内からの直接実行

推奨パス以外でも、固定パスへ依存しないことをリリース前に確認する。

## 20. 検証と文書更新

Windows版の構成変更後は、少なくとも次を確認する。

- ZIPを新しい場所へ展開
- `start-uiap.cmd`から起動
- MSYS2が存在せず、参照もされない
- `UIAP_DEVKIT_ROOT`
- `UIAP_WORKSPACE`
- PATH
- `setup`
- `doctor`
- `versions`
- `make clean`
- `make`
- `make flash`
- USB再列挙
- `make app`
- USB切断
- OS設定復元
- コンソール再起動後の再現
- オンライン`setup`の初回取得、再実行、正常キャッシュ再利用
- 別PCと別ユーザー
- リリースZIPの不要物
- ライセンスとSHA-256

検証結果は`70_VALIDATION_RESULTS.md`へ記録する。

Windows標準構成または`ch32fun`サブセット方針を変更した場合は、`90_DECISIONS.md`、`15_CH32FUN_SUBSET_RULES.md`、ビルド規約、リリースチェックリスト、トラブルシューティングを同時に更新する。

分割文書更新後に`99_FULL_PROJECT_GUIDE.md`を再生成する。


## 21. Windows版の展開先パス制約

Windows版Devkitの展開先は、ローカルドライブ上のASCII・空白なしパスに限定する。

各フォルダー名に使用できる文字:

```text
A-Z a-z 0-9 _ - .
```

ドライブ文字、コロン、バックスラッシュはWindowsパスの構文として使用する。ドライブ直下の1階層だけでなく、同じ条件を満たす複数階層を許可する。

有効な例:

```text
C:\uiap\uiap-devkit-win64
C:\pj\uiap-devkit-win64
C:\pj\xpfes2026\uiap-devkit-win64
D:\work\xpfes2026\uiap-devkit-win64
```

非対応:

```text
C:\Users\User\My Projects\uiap-devkit-win64
C:\Users\User\デスクトップ\uiap-devkit-win64
C:\開発\uiap-devkit-win64
\\server\share\uiap-devkit-win64
```

理由:

- GNU Makeの`include`は、展開後のファイル名に含まれる空白を複数ファイルの区切りとして解釈する
- ビルドはCommand Prompt、Windows PowerShell、GNU Make、xPack `sh.exe`、RISC-V GCCをまたぐ
- 全角文字と非ASCII文字は、各ツールのWindows API、ロケール、文字コード処理が一致することを保証できない
- 1.5時間のワークショップでは、任意パス対応より早期検出と確実な復旧を優先する

### 21.1 パス判定の実装規則

パス判定は`scripts/path-check.ps1`へ集約する。`start-uiap.cmd`、`setup.ps1`、`doctor.ps1`に独立した正規表現を重複実装しない。

`setup.ps1`と`doctor.ps1`は、共通の`path-check.ps1`を呼び出し、終了コードをそのまま扱う。

判定では、少なくとも次を区別する。

- ローカルドライブか
- UNCパスではないか
- Devkitルートまでの全フォルダー要素がASCIIか
- 空白を含まないか
- 各フォルダー要素が半角英数字、ドット、ハイフン、アンダースコアだけか
- 1階層以上の任意の複数階層を正しく処理できるか

正規表現を使用する場合の概念例:

```powershell
$asciiSafePattern = '^[A-Za-z]:\\[A-Za-z0-9._-]+(?:\\[A-Za-z0-9._-]+)*$'
```

正規表現だけに依存せず、`[System.IO.Path]::GetFullPath()`で正規化し、UNC判定と各パス要素の検査を分離することを推奨する。

### 21.2 test11の回帰不具合

Devkit `0.4.3-test11`では、パス検査用の正規表現がWindowsのバックスラッシュと複数階層を正しく表現していなかった。そのため、次の有効なパスも`UIAP-E103`で拒否した。

```text
C:\pj\xpfes2026\uiap-devkit-win64
```

これはフォルダー名の問題ではなく、判定処理の実装ミスである。`0.4.3-test11`はWindows版リリース候補として使用しない。

修正版は、少なくとも次を実機確認してから配布する。

- `C:\uiap\uiap-devkit-win64`で起動、`setup`、`doctor`が成功
- `C:\pj\uiap-devkit-win64`で起動、`setup`、`doctor`が成功
- `C:\pj\xpfes2026\uiap-devkit-win64`で起動、`setup`、`doctor`が成功
- 空白を含むパスを`UIAP-E103`で拒否
- 全角文字を含むパスを`UIAP-E103`で拒否
- UNCパスを`UIAP-E103`で拒否
- エラー本文が日本語

実際に非対応パスである場合だけ`UIAP-E103`を表示し、`setup`、ダウンロード、展開、ビルドを開始しない。

フォルダーを移動した後は、古いコンソールを閉じ、移動先の`start-uiap.cmd`から新しいコンソールを起動する。

## 22. 2026-07-31 macOS test10～test12構成更新

`uiap-devkit-macarm64`では、必須演習3本を`workspace/exercises`へ配置する。

- `00_onboard_led_blink`: macOS実機合格
- `01_macro_keyboard`: test10でmacOS実機合格
- `02_rotary_cursor_size`: test12でmacOS実機合格

`01_macro_keyboard`では、Device Descriptorのクラス値を`0`とし、HIDクラスはInterface Descriptorで宣言する。Boot Keyboardの`GET_REPORT`、`GET_IDLE`、`SET_IDLE`、`GET_PROTOCOL`、`SET_PROTOCOL`をファームウェア側で処理する。

`02_rotary_cursor_size`のmacOSホストは次へ配置する。

```text
workspace/exercises/02_rotary_cursor_size/host/cursor_size_host.c
```

主催者が生成した成果物は次へ配置する。

```text
runtime/bin/uiap-cursor-host
runtime/bin/uiap-cursor-host.build-info
```

test11では、演習02のDevice DescriptorとHID制御要求をmacOS向けに修正し、`1209:C004`のIOHID列挙とCW／CCW受信まで確認した。ただし、非公開CoreGraphicsカーソルAPIのスカラーABIを誤って固定したため、現在値を`0.00`と誤読し、サイズ変更に失敗した。

test12のネイティブホストは次を実装する。

- `CGSGetCursorScale`の書込み幅から`float32`／`float64` ABIを実行時判定
- 判定したABIで`CGSSetCursorScale`を呼び出す
- 現在値の同値書込みと再読取りによる`make host-doctor`
- 非有限値、`0.00`、観測範囲外値を状態ファイルへ保存しない
- サイズ変更後と復元後の再読取り検証
- 正常終了、エラー終了、USB切断時に保存値の復元を試行

macOS 26.5.2の利用者実機で、CW／CCW入力、カーソルサイズ変更、`Ctrl+C`終了時復元が想定どおり動作した。USB切断時復元は未確認である。

参加者向け最終ZIPでは、生成用`runtime/build`やXcode Command Line Toolsを要求する手順を含めない。オンライン`setup`用の空または実行時生成されるダウンロードキャッシュ領域は使用してよい。非公開APIのため、別Mac、別ユーザー、macOS 26以降、OS更新後の回帰確認をリリース判定へ含める。

## 16. Windowsオンライン取得処理の配置

Windowsオンライン初期化型Devkitでは、ダウンロード責務を次へ分離する。

```text
scripts/
├── bootstrap.lock.json
├── download-file.ps1
└── setup.ps1

runtime/downloads/
├── <archive>
├── <archive>.part
└── <archive>.bad-YYYYMMDD-HHMMSS
```

| 項目 | 責務 |
|---|---|
| `bootstrap.lock.json` | コンポーネント名、固定URL、SHA-256、インストール種別、展開先 |
| `download-file.ps1` | `curl.exe`実行、進捗、再試行、再開、ハッシュ検証、キャッシュ採用 |
| `setup.ps1` | 固定ロックの順次処理、展開、サブセット生成、インストール状態記録 |
| `runtime/downloads/*.part` | 中断・失敗した未完了データ。再実行時の再開候補 |
| `runtime/downloads/*.bad-*` | SHA-256不一致として隔離したデータ |

`download-file.ps1`はPowerShellの`curl`別名を使用せず、`%SystemRoot%\System32\curl.exe`を優先して実行する。curlの進捗表示はコンソールへ直接出し、セットアップログには開始、成功、終了コード、SHA-256結果だけを記録する。

最終参加者向けZIPの初期状態では、`runtime/downloads`の取得済みアーカイブ、`.part`、`.bad-*`を除外する。最終版の`setup`は同ディレクトリを実行時キャッシュとして使用してよい。

### 16.1 `0.5.0-test13`の範囲

`uiap-devkit-win64` `0.5.0-test13`は、ダウンロード進捗方式を統合した主催者検証版である。

含むもの:

- xPack Windows Build Tools、xPack RISC-V GCC、Python、hidapi、ch32funの固定取得定義
- `setup`、`doctor`、`versions`、`report`
- `00_onboard_led_blink`のソースとMakefile

未統合:

- 固定済み`rv003usb`
- 既存の検証済み`01_macro_keyboard`実装
- 既存の検証済み`02_rotary_cursor_size`実装

必須演習の決定は変更しない。test13の未統合状態を最終参加者向け構成として採用しない。

## 23. Windows起動シェルの配置と呼出し

`start-uiap.cmd`はDevkit内ツールをPATHの先頭へ追加するが、Windows標準システムディレクトリを失ってはならない。

標準実体:

```text
%SystemRoot%\System32\cmd.exe
%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe
```

起動ファイルと`scripts/cmd/*.cmd`は、上記を絶対パスで呼び出す。PATHには少なくともSystem32、Wbem、Windows PowerShellを保持する。`cmd.exe /K`起動失敗時は`UIAP-E105`と終了コードを表示し、ダブルクリックしたウィンドウを即時終了させない。

## 2026-08-01 Windows test17 HID演習再統合

`uiap-devkit-win64` `0.6.0-test17`では、`01_macro_keyboard`と`02_rotary_cursor_size`のプレースホルダーを実装済みソースへ置き換える。

追加する構成:

```text
workspace/exercises/01_macro_keyboard/
├── Makefile
├── README.md
├── macro_keyboard.c
├── funconfig.h
├── usb_config.h
└── host/hidcheck.py

workspace/exercises/02_rotary_cursor_size/
├── Makefile
├── README.md
├── rotary_cursor_size.c
├── funconfig.h
├── usb_config.h
└── host/cursor_size_host.py
```

`rv003usb`は`workspace/deps/rv003usb`へ配置する。test17では固定コミットのRaw URLからコア3ファイルとMITライセンスを取得する主催者検証方式とする。最終参加者向け版でも現在のオンライン取得形式を維持し、ファイル単位SHA-256を正式固定する。

実機検証状態は`70_VALIDATION_RESULTS.md`を正本とする。

<!-- Source: 15_CH32FUN_SUBSET_RULES.md -->

# ch32fun参加者向けサブセット規約

更新日: 2026-08-01

## 1. 目的

この文書は、XP祭り2026の参加者向けUIAP Devkitへ同梱する`ch32fun`を、固定済み上流ソースから許可リスト方式で生成するための規約を定める。

目的:

- UIAPduino Pro Micro CH32V003 V1.4で必要なファイルだけを配布する
- 他MCU向けサンプルによる混乱と誤操作を減らす
- 配布ファイル数、展開時間、スキャン対象を減らす
- 上流ソース、ローカル変更、配布サブセットの対応関係を追跡可能にする
- 手作業による削除漏れ、必要ファイルの誤削除、担当者差を防ぐ

この方針は、参加者向け配布物を対象とする。主催者用の完全な上流ソース保管を禁止しない。

## 2. 基本原則

参加者向け`ch32fun`は、完全な上流ツリーをコピーして不要物を削除する方式ではなく、固定済み上流ツリーから許可されたパスだけを新しいディレクトリへコピーして生成する。

原則:

- デフォルト拒否とする
- 許可リストへ記載されていないファイルは配布しない
- 上流コミット、取得元、入力アーカイブSHA-256を固定する
- 生成処理をスクリプト化する
- 同じ入力から同じサブセットを再生成できるようにする
- 生成後に必須ファイルと禁止ファイルを自動検査する
- Windows版とmacOS版で同一の`ch32fun`ソースサブセットを使用する
- OS固有の実行バイナリは`runtime`側で管理し、ソースサブセットと混同しない

## 3. 固定する上流情報

現行の検証基準:

```text
Upstream: cnlohr/ch32fun
Commit: 1e4887e11d4bfa739ed5604524b69f5be9f9275b
License: MIT
```

上流コミットを変更する場合は、許可リスト、生成結果、ライセンス、全演習のビルドと書き込みを再検証する。

## 4. リリース元の管理ファイル

参加者向けZIPの外側にあるリリース元リポジトリで、少なくとも次を管理する。

```text
release/ch32fun/
├── allowlist.txt
├── required-paths.txt
├── forbidden-paths.txt
├── make-subset.py
├── verify-subset.py
├── upstream.json
├── patches/
└── README.md
```

役割:

| ファイル | 用途 |
|---|---|
| `allowlist.txt` | 配布を許可する上流相対パスの一覧 |
| `required-paths.txt` | 生成後に必ず存在すべきパス |
| `forbidden-paths.txt` | 生成後に存在してはならないパスまたはパターン |
| `make-subset.py` | 完全版上流ツリーからサブセットを生成 |
| `verify-subset.py` | 許可外ファイル、欠落、ハッシュ、改行などを検査 |
| `upstream.json` | 配布元、コミット、取得日、入力SHA-256、ライセンス |
| `patches/` | 上流へ適用するローカルパッチ。変更がない場合は空でよい |
| `README.md` | 再生成手順、必要ツール、期待結果 |

ファイル名や配置を変更する場合も、同等の情報と自動化を維持する。

## 5. 参加者向けサブセットの構成

`workspace/deps/ch32fun`には、上流由来の必要ファイルと、サブセット識別用メタデータだけを配置する。

概念上の構成:

```text
workspace/deps/ch32fun/
├── LICENSE
├── README.md
├── SUBSET.md
├── UPSTREAM_COMMIT
├── ALLOWLIST.txt
├── ch32fun/
├── minichlink/
├── misc/
└── extralibs/
```

上記はディレクトリ単位の無条件許可を意味しない。実際に含めるファイルは`allowlist.txt`へ相対パス単位で記載する。

### 5.1 必須候補

少なくとも次を許可リスト候補として評価する。

- ルート`LICENSE`
- ルート`README.md`
- `ch32fun/ch32fun.c`
- `ch32fun/ch32fun.h`
- `ch32fun/ch32fun.mk`
- `ch32fun/ch32fun.ld`
- `ch32fun`以下でCH32V003のビルドに必要なヘッダー、リンカースクリプト、補助ファイル
- `minichlink`以下で配布する書き込みツールのビルドまたはライセンス確認に必要なファイル
- `misc/libgcc.a`など、採用ツールチェーンで実際に参照されるファイル
- `extralibs`以下で採用演習が実際に参照するファイル

必要性は、Makefileの静的確認だけで決めず、クリーン環境でのビルド、書き込み、診断によって確認する。

### 5.2 生成時に追加するメタデータ

次は上流ソースからのコピーではなく、リリース処理が生成してよい。

- `SUBSET.md`
- `UPSTREAM_COMMIT`
- `ALLOWLIST.txt`
- サブセット生成ツールのバージョン
- 入力アーカイブSHA-256
- ローカルパッチ一覧

`SUBSET.md`には、上流、コミット、ライセンス、サブセットであること、完全版対応ソースの入手方法を記載する。

## 6. 原則として配布しない上流領域

UIAPduino Pro Micro CH32V003 V1.4向け参加者キットでは、次を許可リストへ追加しない。

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
.gitignore
.gitmodules
.clang-format
```

理由:

- 他MCU向けまたは上流開発者向けで、参加者演習のビルドに不要
- UIAPduinoで使用できないハードウェアUSB、BLE、CAN、Ethernet、USB PDなどを含む
- PlatformIOと上流一括ビルドは参加者向け標準環境では使用しない
- 不要な選択肢、ファイル数、監査対象を増やす

将来、採用演習で特定ファイルが必要になった場合は、ディレクトリ全体ではなく、必要なファイルを個別に許可し、理由と検証結果を記録する。

## 7. ライセンスと対応ソース

`ch32fun`のサブセット配布では、少なくとも次を行う。

- 上流のMIT `LICENSE`をサブセット内に保持する
- `licenses/COMPONENTS.csv`または同等の一覧へ`ch32fun`を記載する
- 上流リポジトリ、固定コミット、ライセンス、サブセットであることを記載する
- ローカル変更がある場合はパッチとして保存する
- 対応ソースアーカイブに、完全な固定コミットの上流ソース、パッチ、許可リスト、生成スクリプト、再生成手順を含める
- `SHA256SUMS`へ参加者向けZIP、対応ソース、SBOMを記載する

参加者向けZIPに完全な上流ツリーを同梱する必要はないが、配布物を再現できる情報はリリース元で保持する。

`ch32fun`以外のGCC、Make、Python、hidapi、libusb、`rv003usb`などのライセンス義務は別途確認する。

## 8. SBOMと来歴

SBOMでは、完全版上流ソースと参加者向けサブセットを混同しない。

記録候補:

- コンポーネント名: `ch32fun`
- 上流コミット
- 上流取得元
- 上流入力アーカイブSHA-256
- 配布形態: `subset`
- サブセット生成規則の識別子またはバージョン
- サブセット全体またはファイルマニフェストのSHA-256
- ローカルパッチ
- ライセンス

## 9. セキュリティ要件

生成処理では次を確認する。

- 入力アーカイブのSHA-256が固定値と一致する
- ZIP Slipなどを避け、安全な一時ディレクトリへ展開する
- シンボリックリンクを配布しない
- 許可リストのパスに`..`、絶対パス、ドライブ文字を認めない
- 許可されたパスが上流ルート外へ解決されない
- 同名ファイルの大文字小文字衝突を検出する
- Windows予約名を検出する
- 実行ファイル、バイナリ、アーカイブを意図せず追加しない
- 許可外ファイルが生成後ツリーに存在した場合はリリースを失敗させる
- 必須ファイルが欠けた場合はリリースを失敗させる
- サブセット生成後にマルウェアスキャンとシークレットスキャンを実施する
- 生成用一時ディレクトリ、ログ、ダウンロードキャッシュを参加者向けZIPへ含めない

## 10. 生成処理の要件

推奨フロー:

1. 固定URLまたは保存済みアーカイブから上流ソースを準備
2. 入力SHA-256を検証
3. 新しい空ディレクトリを作成
4. `allowlist.txt`に記載されたファイルだけをコピー
5. 必要なローカルパッチを適用
6. `SUBSET.md`、`UPSTREAM_COMMIT`、`ALLOWLIST.txt`を生成
7. 許可外ファイル、欠落、パス規約、改行を検査
8. 全採用演習をクリーンビルド
9. 書き込み、USB列挙、HID、ホストアプリを検証
10. `manifest.sha256`、SBOM、対応ソースを生成
11. 別の空ディレクトリでも再生成し、ファイル一覧とハッシュが一致することを確認

サブセットを手作業で編集しない。変更は上流コミット、許可リスト、パッチ、生成スクリプトのいずれかへ反映する。

## 11. ビルド検証

Windows 11 x64とmacOS Apple Siliconで、各採用演習について次を確認する。

```sh
make clean
make
make size
make flash
```

ホストアプリを使用する場合:

```sh
make hidcheck
make app
make restore
```

追加確認:

- `CH32FUN_ROOT`がサブセットの`workspace/deps/ch32fun`を参照する
- `ch32fun/ch32fun.mk`、リンカースクリプト、必要ヘッダーが見つかる
- `minichlink`または配布済み書き込みツールが正常に動作する
- `misc/libgcc.a`を参照する場合は存在する
- 除外したexamples、projects、PlatformIO設定への参照がない
- 最終オンライン`setup`で取得・生成したサブセットを使用してビルドと書き込みが成功する
- 完全版上流ツリーへフォールバックしていない

## 12. 検証状態

2026-07-31時点:

- 許可リスト方式の採用: 決定済み
- 最終レビュー済み許可リストと生成スクリプト: 未確認
- Windowsでの最終許可リスト版ビルド・書き込み: 未確認
- macOSでの現行テストサブセットによる必須演習3本のビルド・書き込み: 確認済み
- macOSでの最終許可リスト版ビルド・書き込み: 未確認
- オフライン最終ZIP: 未確認
- SBOMと対応ソースの生成: 未確認

実装と検証結果は`70_VALIDATION_RESULTS.md`へ記録する。
## 13. 2026-07-29 macOS Apple Siliconでの暫定サブセット確認

主催者検証版`uiap-devkit-macarm64` `0.1.7-test8`では、最終レビュー済み許可リストではないテストサブセットを使用した。macOS 26.5.2、Apple Silicon arm64で、次を確認した。

- `ch32fun`上流コミット`1e4887e11d4bfa739ed5604524b69f5be9f9275b`の取得
- `ch32fun/ch32fun.c`、`ch32fun.h`、`ch32fun.ld`、`misc/libgcc.a`など、Lチカ演習に必要なパスの解決
- `00_onboard_led_blink`のクリーンビルド
- FLASH 444 B、RAM 0 B
- ELF、BIN、HEX、LST、MAPの生成
- `runtime/bin/minichlink`を使った`make flash`
- USBブートローダー`1209:B803`とCH32V003の検出
- 書き込み、ブート、基板上LEDの物理点滅

この結果は、当該テストサブセットがLチカ演習のビルドと書き込みに足りたことだけを示す。次を確認したことにはならない。

- 最終許可リストのレビュー完了
- 全採用演習のビルド
- HIDアプリケーション列挙とHID送受信
- Windows版とmacOS版で同一生成物になること
- 対応ソース、SBOM、再生成性
- オフライン最終ZIP

`doctor`では、最終許可リストでないことを警告として残す。参加者向けリリース判定では、この警告を解消する。

## 16. macOS版minichlink主催者ビルドとの境界

`uiap-devkit-macarm64` `0.1.7-test8`では、主催者専用`build-minichlink`が固定コミットの完全な`ch32fun`ソースアーカイブから`minichlink`を生成した。

実機で観測した入力SHA-256:

```text
ch32fun source archive: 37a507fa58710a14dbd3e959def57b02a6b0b1d410c9e307653e22aeb081ba9f
libusb 1.0.29 archive: 5977fc950f8d1395ccea9bd48c06b3f808fd3c2c961b44b0c2e6e29fc3a70a85
```

この主催者ビルド用完全ソースと、参加者向け`workspace/deps/ch32fun`サブセットを混同しない。

- 主催者リリース元: 完全な固定コミット、libusbソース、パッチ、ビルドスクリプト、入力SHA-256を保持する
- 参加者向けZIP: 採用演習のビルドに必要な許可リストサブセットと、検証済み`runtime/bin/minichlink`を格納する
- `runtime/build`、主催者用一時ファイル、完全なダウンロードキャッシュを参加者向けZIPへ含めない
- 参加者向けサブセットに`minichlink`ソースを含めるかは、ライセンス、対応ソース提供、復旧性、サイズを評価して明示的に決定する

`test8`の`doctor`では、現行`ch32fun`を「test subset」として警告している。HID演習を含む全採用演習のビルドと書き込みを確認するまで、最終許可リストとして合格にしない。

## 17. 2026-07-31 test9のNewlib検査漏れとtest10修正

`0.1.8-test9`の`doctor`は、インストール済みサブセットに`-I/usr/include/newlib`がないと表示した。しかし、`01_macro_keyboard`の実コンパイル行には同オプションが残っていた。

これは、検査対象と実際にGNU Makeが読み込むビルド設定が一致していなかったためであり、test9のPASS判定を訂正する。

`0.1.9-test10`では次を行う。

- `ch32fun.mk`由来の`-I$(NEWLIB)`をサブセット生成時に除去
- サブセット内の`-I$(NEWLIB)`と`/usr/include/newlib`を再帰検索
- 必須演習3本について`make -n build`を実行
- dry-runに`/usr/include/newlib`が現れた場合は`doctor`をFAIL

macOS実機では、test10で`00_onboard_led_blink`と`01_macro_keyboard`が動作した。test11／test12では同じテストサブセットを使用して`02_rotary_cursor_size`のビルド、書き込み、USB・IOHID列挙、CW／CCW受信、カーソルサイズ変更、`Ctrl+C`終了時復元を確認した。実際のコンパイル行に`-I/usr/include/newlib`がないことも確認した。

この結果は、現行テストサブセットがmacOS上の必須演習3本に足りたことを示すが、最終レビュー済み許可リストであること、Windowsと同一の生成規則で再生成できること、対応ソース、SBOM、オフライン性を保証しない。参加者向け最終リリースでは、最終許可リストを両OSで検証し、対応ソース、SBOM、再生成性を確定する。

## 18. ch32fun入力アーカイブの形式とSHA-256

同じ上流コミットでも、ZIPとtar.gzは別の入力ファイルとして管理する。SHA-256は展開後のソースツリーではなく、実際に取得したアーカイブ全体へ対応させる。

現行の検証値:

| 用途 | 形式 | SHA-256 |
|---|---|---|
| Windowsオンライン検証版 | ZIP | `30e13fcf4c123981d0fba99a01a31cda30f57757356057bdce2e6cad026f58b1` |
| macOS test8主催者ビルド | tar.gz | `37a507fa58710a14dbd3e959def57b02a6b0b1d410c9e307653e22aeb081ba9f` |

ロック情報には、少なくともコミット、取得URL、保存ファイル名、`archive_format`、SHA-256を記録する。形式が異なるハッシュを流用しない。一般的な取得物の固定規則は`20_BUILD_RULES.md`、リリース検査は`50_RELEASE_CHECKLIST.md`を正本とする。

`uiap-devkit-win64` `0.5.2-test15`はZIPを取得しながらtar.gzのSHA-256を期待したため、`UIAP-E122`で停止した。`0.5.3-test16`ではWindows用ZIPのロックを修正し、隔離済みファイルを新しい期待値で再検証できるようにした。実機観測と検証状態は`70_VALIDATION_RESULTS.md`に記録する。

<!-- Source: 20_BUILD_RULES.md -->

# ビルド、Makefile、ファイル規約

更新日: 2026-08-01

## 1. 基本方針

Windows 11 x64とmacOS Apple Siliconで、同じソースコード、Makefile、演習コマンドを使用する。

OS固有差異は、起動ファイル、環境変数、PATH設定、補助スクリプトの内部へ閉じ込める。

Windows版の標準ランタイムは、MSYS2を使用しないxPackベースのWindowsネイティブ構成とする。

- xPack Windows Build Tools
- xPack GNU RISC-V Embedded GCC
- Windows Command Prompt
- PowerShell補助スクリプト
- 同梱Pythonとhidapi

過去のMSYS2 UCRT64構成は検証履歴として残すが、現行の参加者向け手順、Makefile、復旧方法へ混用しない。

参加者向け最終配布版もオンライン・ブートストラップ方式とする。初回`setup`ではインターネット接続を使用して固定済み入力を取得するが、管理者権限やHomebrew、Xcode Command Line Tools、システムPythonなどの追加インストールは前提にしない。取得URL、バージョン、アーカイブ形式、SHA-256を固定する。

macOS Apple Siliconの主催者検証版`0.1.7-test8`では、Devkit内部のxPack GNU RISC-V Embedded GCC 14.2.0-3 arm64とGNU Make 4.4.1 arm64を使用し、固定ソースからarm64版`minichlink`を生成して、CH32V003への書き込みと基板上LEDの物理動作まで確認した。これはPython・hidapi、HIDホストアプリ、オフライン配布、別Macでの確認を意味しない。

検証結果は`70_VALIDATION_RESULTS.md`へ記録する。

## 2. 参加者が使用する共通コマンド

環境起動後は、両OSで原則として次を使用する。

```sh
make
make flash
make clean
```

演習にホスト側プログラムが含まれる場合は、次を共通候補とする。

```sh
make app
make doctor
make report
```

演習固有の確認用ターゲットとして、必要に応じて次を追加してよい。

```sh
make size
make hidcheck
make restore
make help
```

追加ターゲットが必要な場合も、既存ターゲットの意味を変更しない。

参加者は、Windowsではトップレベルの`start-uiap.cmd`、macOSでは`start-uiap.command`から開発環境を起動する。起動後は受講者自身が`cd`で対象演習へ移動する。参加者にランタイムの選択、Python venvのactivate、書き込みツールの直接指定を行わせない。

演習移動用の`sample`、`macro`、`blink`や、特定演習用の`cursorapp`、`cursorlist`、`cursorrestore`などをトップレベルコマンドとして提供しない。演習固有操作は、その演習のMakefileターゲットへ置く。

コマンド例にはプロンプト記号を含めず、そのままコピーできる形式にする。

### 2.1 演習ディレクトリへの移動

Windows Command Prompt:

```text
cd /d "%UIAP_WORKSPACE%\exercises\02_rotary_cursor_size"
```

macOS:

```sh
cd "$UIAP_WORKSPACE/exercises/02_rotary_cursor_size"
```

移動後に、同じ演習ディレクトリで次を実行する。

```sh
make clean
make
make flash
make hidcheck
make app
```

`cd`と`make`を別の意味を持つ独自コマンドへ隠さない。現在のディレクトリを`cd`または`pwd`で確認できる構成を優先する。

## 3. 共通環境変数

必須:

```text
UIAP_DEVKIT_ROOT
UIAP_WORKSPACE
```

必要に応じて使用:

```text
UIAP_RUNTIME
UIAP_TOOLCHAIN_BIN
UIAP_FIRMWARE
UIAP_PYTHON
```

必要な環境変数が設定されていない場合は、処理を継続せず、起動方法を含む明確なエラーを表示する。

```make
ifndef UIAP_WORKSPACE
$(error UIAP_WORKSPACE is not set. Start the UIAP development environment first)
endif
```

環境変数へ開発者固有の固定パスを埋め込まない。

## 4. Makefileの依存パス

不安定な相対パスだけで外部依存を参照しない。

廃止対象例:

```make
CH32FUN = ../ch32fun
RV003USB = ../rv003usb
```

推奨:

```make
CH32FUN_ROOT ?= $(UIAP_WORKSPACE)/deps/ch32fun
CH32FUN ?= $(CH32FUN_ROOT)/ch32fun
RV003USB_ROOT ?= $(UIAP_WORKSPACE)/deps/rv003usb
RV003USB ?= $(RV003USB_ROOT)
```

依存関係の実際の展開構造は、固定したコミットまたはリリースに合わせる。`workspace/deps/VERSIONS.md`と一致させる。

## 5. Windowsパスの正規化

Windowsの環境変数は、次の形式になる場合がある。

```text
C:\pj\uiap-devkit-win64
```

GNU MakeからPOSIX互換`sh`へパスを渡す場合は、Makefile内部で次の形式へ正規化する。

```text
C:/pj/uiap-devkit-win64
```

例:

```make
UIAP_DEVKIT_ROOT_POSIX := $(subst \,/,$(UIAP_DEVKIT_ROOT))
UIAP_WORKSPACE_POSIX := $(subst \,/,$(UIAP_WORKSPACE))

CH32FUN_ROOT := $(UIAP_WORKSPACE_POSIX)/deps/ch32fun
CH32FUN := $(CH32FUN_ROOT)/ch32fun
RV003USB := $(UIAP_WORKSPACE_POSIX)/deps/rv003usb
```

環境変数自体はWindows形式のまま保持してよい。正規化は、MakefileやPOSIX互換シェルへ渡す箇所だけで行う。

次のようにバックスラッシュが消えたパスを生成してはならない。

```text
C:pjuiap-devkit-win64workspace...
```

`doctor`またはリリース検査で、少なくとも次を確認する。

- `make -n`で外部コマンドへ渡されるパスが`C:/...`形式
- `generated__.ld`の出力先が存在する
- 展開先変更後も固定パスへ依存しない

## 6. Makefileで固定してはいけないもの

- Windowsのドライブ文字
- バックスラッシュ区切りの絶対パス
- macOSのホームディレクトリ
- 特定ユーザー名
- 開発者個人のホーム
- ZIPの展開先
- 特定PCのUSBデバイスインスタンスID
- 特定環境だけに存在するPATH
- PoC実機で取得したMCU UUID
- 一時USBシリアル番号

## 7. ターゲット名と責務

標準ターゲット:

- `make`: 通常ビルド
- `make flash`: ビルド済みファームウェアの書き込み
- `make clean`: 当該演習の生成物削除
- `make size`: メモリ使用量表示
- `make help`: ターゲット説明

ホストアプリを伴う演習:

- `make app`: 配布環境内のホストアプリをフォアグラウンドで起動
- `make hidcheck`: 対象HIDデバイスの列挙確認
- `make list`: 当該演習が対象とするHIDデバイスを列挙
- `make app-dry-run`: OS設定を変更せず、当該演習の入力イベントを確認
- `make restore`: ホストアプリが変更したOS設定を復元
- `make report`: 講師または生成AIへ渡す診断情報を生成
- `make doctor`: 演習固有の自己テスト
- `make adc-monitor`: OS設定と出力部品を変更せずADC値を監視
- `make haptic-test`: 振動プロファイルを単独確認
- `make cursor-test`: HID入力と分離してOS設定変更だけを確認

デバイス制御演習では、必要に応じて次を追加してよい。

- `make on`
- `make off`
- `make status`

`make flash`、`make app`、`make restore`のOS固有処理は補助スクリプト内部へ閉じ込める。

### 7.1 トップレベル別名コマンドを作らない

演習固有の処理を`scripts/cmd`のグローバルコマンドへ複製しない。

不採用例:

```text
sample
macro
blink
hidcheck
cursorapp
cursorlist
cursorrestore
cursorstore
```

対応する標準操作:

| 旧別名・候補名 | 標準操作 |
|---|---|
| `sample` | 対象演習へ`cd` |
| `macro` | `01_macro_keyboard`へ`cd`して`make` |
| `blink` | `00_onboard_led_blink`へ`cd`して`make` |
| `hidcheck` | 対象演習で`make hidcheck` |
| `cursorapp` | `02_rotary_cursor_size`で`make app` |
| `cursorlist` | 同演習で`make list` |
| `cursorrestore` / `cursorstore` | 同演習で`make restore` |

Devkit共通の`setup`、`doctor`、`versions`、`report`はトップレベルコマンドとしてよい。

## 8. ターゲット名とソースファイル

`TARGET`を指定するビルドシステムでは、主ソースファイル名との対応を明確にする。

```make
TARGET := example_device
```

ビルドシステムが`$(TARGET).c`を暗黙に要求する場合、次が必要になる。

```text
example_device.c
```

主ソース名を一致させない場合は、ソース一覧をMakefileへ明示する。

ビルド前またはエラー時に確認する。

- `TARGET`の値
- 主ソースファイルの存在
- 大文字と小文字
- 拡張子
- 実行ディレクトリ
- 追加ソースとインクルードパス

## 9. UIAPduino V1.4のUSBブートローダー書き込み

Windows 11 x64で、UIAPduino Pro Micro CH32V003 V1.4のUSBブートローダーと`minichlink`を使用した書き込みを実機確認済みである。

ブートローダーVID:PID:

```text
1209:B803
```

参加者向け操作は`make flash`へ統一する。`minichlink`の内部コマンドを参加者へ入力させない。

書き込み処理は、原則として次を行う。

1. 対象ファームウェアをビルド
2. 現在接続中の物理USBブートローダーを列挙
3. 物理ブートローダーが1台だけであることを確認
4. `minichlink`で書き込み
5. アプリケーションの再列挙を待機
6. 期待VID:PID、製品名、必要ならUSBシリアル番号を確認
7. 失敗時にフォールバック手順を表示

1台の物理ボードが親USBデバイスと複数のHID子デバイスとして列挙される場合がある。物理ボード数は、`USB\VID_1209&PID_B803\...`形式の現在接続中の親デバイス単位で判定する。

複数の物理ブートローダーを検出した場合は書き込みを中止する。自動で最初の1台を選択しない。

書き込み成功の代表表示:

```text
VID:0x1209, PID:0xb803
Detected CH32V003
Image written.
Booting
```

ブートローダーのVID:PIDと通常アプリケーションのVID:PIDを混同しない。

## 10. アプリケーションVID:PIDとUSB識別子

USBアプリケーションを作成する場合、次の値を同一リリース内で一致させる。

- ファームウェアのDevice Descriptor
- PC側ホストプログラム
- Makefileまたは補助スクリプト
- READMEと参加者向け手順
- USB列挙確認スクリプト
- `70_VALIDATION_RESULTS.md`

PoCで使用した一時値の例:

```text
1209:C003
1209:C004
1209:D003
TEST3-001
TEST7-001
```

これらは正式な公開配布用識別子として決定されていない。公開配布または製品化へ流用しない。

同一VID:PIDの複数台を扱う場合は、正式に検証したUSBシリアル番号とUsage Page、Usage、製品名、デバイス役割を使用して選択する。

## 11. PowerShell、Command Prompt、Pythonの境界

PowerShell、Command Prompt、Pythonで引用符の解釈が重なるため、複雑なPythonコードを`python -c`で実行しない。

不採用例:

```powershell
& $Python -c "import hid; print(\"hidapi import: PASS\")"
```

推奨:

```powershell
& $PythonPath "$Root\scripts\python\hidapi_probe.py"
```

外部プログラムは、可能な限り文字列連結したシェルコマンドではなく、引数配列として実行する。

Python例:

```python
args = [
    minichlink_path,
    "-c", "0x1209b803",
    "-w", image_path,
    "flash",
    "-b",
]
subprocess.run(args, check=True)
```

診断コード、USB列挙コード、設定復元コードは、テスト可能な`.py`または`.ps1`ファイルへ分離する。

## 12. ホスト側Pythonアプリ

### 配置規則

PC側Pythonプログラムは、対応する演習の`host`ディレクトリへ配置する。

```text
workspace/exercises/<exercise-name>/host/<program>.py
```

例:

```text
workspace/exercises/02_rotary_cursor_size/host/cursor_size_host.py
```

次を標準とする。

- トップレベルの`workspace/host`を使用しない
- PC側プログラムがない演習に空の`host`を作成しない
- 演習の`Makefile`は、その演習ディレクトリを基準に`host`を参照する
- 別演習の`host`を直接参照しない
- `scripts/python`には、Devkit全体で使用する診断、USB列挙、復旧などの補助プログラムだけを置く

`make app`の概念例:

```make
HOST_APP := host/cursor_size_host.py

app:
	"$(UIAP_PYTHON)" "$(CURDIR)/$(HOST_APP)"
```

`UIAP_WORKSPACE/host`や開発者固有の絶対パスを参照しない。

### 実行規則

参加者向けホストアプリは、原則として次を満たす。

- 配布パッケージ内のPythonを使用
- venvのactivate操作を参加者へ要求しない
- USB依存は原則`hidapi`へ限定
- フォアグラウンドで起動
- 終了方法を`Ctrl+C`として明示
- USB切断時に明確なメッセージを表示して終了
- 自動再接続を必須にしない
- サービス、LaunchAgent、ログイン項目を作成しない
- ログを`logs/`へ保存
- 管理者権限を要求しない

OS設定を変更するアプリは、追加で次を満たす。

- 起動前の設定値を保存
- 正常終了時に元へ戻す
- 明示的な復元コマンドを提供
- 異常終了時の手動復旧手順を文書化
- 設定変更失敗とHID受信失敗を区別して表示

## 13. 生成物

通常の生成物例:

```text
*.bin
*.elf
*.hex
*.lst
*.map
*_ext.bin
firmware.bin
```

生成物はソース管理および参加者向けZIPへ原則として含めない。

復旧用など配布理由があるバイナリは`firmware`へ分離し、対象ボード、ビルド元、バージョン、SHA-256、用途を記録する。

ログも参加者向けリリースZIPへ含めない。

## 14. 外部ライブラリとオンライン取得

`ch32fun`、`rv003usb`などは、検証済みコミットまたはリリースに固定する。

`workspace/deps/VERSIONS.md`に次を記録する。

- ライブラリ名
- 配布元
- バージョンまたはコミットID
- 取得日
- SHA-256
- ライセンス
- ローカル変更
- 動作確認OS

オンライン・ブートストラップ方式では、検証版・最終版とも取得URLとSHA-256を固定し、取得済みファイルを再利用できる構成にする。

最終参加者向け配布版でも「最新版」を動的に選ばない。`setup`はロック済み入力だけを取得し、当日の`pip install`、`pacman -S`、Homebrew、任意のGit cloneを標準手順に含めない。

## 15. 文字コードと改行

- 文字コード: UTF-8
- `.c`: LF
- `.h`: LF
- `.py`: LF
- `.ps1`: LF
- `Makefile`: LF
- `.mk`: LF
- `.md`: LF
- `.sh`: LF
- `.cmd`: CRLFを許可
- `.bat`: CRLFを許可

## 16. ファイル名

- 原則として半角英数字、ハイフン、アンダースコアを使用
- 大文字と小文字だけで別ファイルを区別しない
- 末尾に空白やピリオドを使用しない
- シンボリックリンクへ依存しない
- Windows予約名を使用しない

禁止対象例:

```text
CON
PRN
AUX
NUL
COM1
LPT1
```

`nul`というファイルも配布版から削除する。

## 17. `.gitattributes`

推奨例:

```gitattributes
* text=auto

*.c       text eol=lf
*.h       text eol=lf
*.py      text eol=lf
*.ps1     text eol=lf
*.md      text eol=lf
*.sh      text eol=lf
Makefile  text eol=lf
*.mk      text eol=lf

*.cmd     text eol=crlf
*.bat     text eol=crlf

*.bin     binary
*.elf     binary
*.hex     binary
*.png     binary
*.jpg     binary
*.pcapng  binary
*.zip     binary
```

## 18. `.gitignore`

プロジェクトごとに、少なくとも次を除外する。

```gitignore
*.bin
*.elf
*.hex
*.lst
*.map
*_ext.bin
firmware.bin
.DS_Store
Thumbs.db
.vscode/
logs/
.state/
runtime/venv/
```

VS Code設定をプロジェクト共通で配布する場合は、必要なファイルだけ例外指定する。

## 19. シェル、PowerShell、バッチ

### POSIXシェル

- POSIXシェル互換を優先
- `bash`固有機能を使う場合は明示
- `set -eu`または同等のエラー処理
- 自身の配置場所からルートを解決
- カレントディレクトリに依存しない
- パスは引用符で囲む
- 参加者にOS別スクリプトを選択させない

### PowerShell

- `-NoLogo -NoProfile`を使用
- 必要な場合だけ`-ExecutionPolicy Bypass`を起動スクリプトから指定
- PnP列挙では現在接続中の物理親デバイスを判定
- 文字列連結したコマンド実行を避ける
- 終了コードをMakeへ伝搬
- 個人パスや不要なUSB識別子をログへ残さない

### Windowsバッチ

`start-uiap.cmd`は起動処理に限定する。

- `%~dp0`などで自身の場所を取得
- 固定ドライブ文字を使用しない
- 当該Devkitのランタイムを選択
- 参加者の既存PATHを破壊しない
- 初期ディレクトリを`workspace`へ設定
- セットアップ状態と次のコマンドを表示
- 参加者にMSYS2やツールの種類を選ばせない

## 19.1 macOS Apple Siliconのビルドツール

参加者向けmacOS版は、システムの`/usr/bin/make`、Homebrewのインストール済み環境、Xcode Command Line Tools、システムPythonへ依存しない。

主催者検証版`0.1.7-test8`で確認した値:

```text
GNU Make: 4.4.1 arm64
RISC-V GCC: xPack 14.2.0-3 arm64
ch32fun: 1e4887e11d4bfa739ed5604524b69f5be9f9275b
rv003usb: 75d926abe89a3002020b989015eab97ce5ad0470
libusb: 1.0.29 static arm64
minichlink: 38e653f8354ea8fc19da5f2595cf9958d26738e7
```

参加者が実行する`make`は`runtime/bin/make`ラッパーを経由し、Devkit内の`runtime/build-tools/bin/gmake`を起動する。`gmake`が存在しない場合はシステムMakeへフォールバックせず、`UIAP-E202`で停止する。

最終版を含むオンライン・ブートストラップDevkitの`setup`は、固定URL、固定バージョン、アーカイブ形式、SHA-256で主要ツールを取得する。ダウンロード失敗、SHA-256不一致、途中再実行、正常キャッシュ再利用を確認する。

### 19.1.1 主催者用minichlinkビルド

`build-minichlink`は主催者専用とする。主催者用MacではXcode Command Line ToolsのApple clangとSDKを使用してよいが、生成済み成果物を参加者向けDevkitへ格納し、参加者にはビルドを要求しない。

ビルド順序:

1. 固定ソースと入力SHA-256を検証
2. libusbをarm64静的ライブラリとしてビルド
3. `minichlink`をarm64としてリンク
4. 最終配置後に実行権限を設定
5. `runtime/bin/minichlink`単体の隔離属性を除去
6. アドホック署名
7. `codesign --verify`
8. 隔離属性、アーキテクチャ、動的依存を再検査
9. 署名後バイナリのSHA-256と来歴を記録

署名後に`strip`、パッチ、バイナリ編集を行わない。変更が必要な場合は、変更後に再署名・再検証する。

Devkit全体への`xattr -dr`を標準処理にしない。隔離属性処理の対象は、主催者が当該Macでローカル生成した`runtime/bin/minichlink`単体に限定する。

### 19.1.2 依存関係検査

`otool -L`の先頭行は検査対象ファイル自身のパスであり、動的ライブラリ依存ではない。依存検査では先頭行を除外してから、次を拒否する。

```text
/opt/homebrew/
/usr/local/
/Users/<developer>/
動的libusb
```

許可するのは、配布方針で認めたmacOSシステムライブラリとフレームワークだけとする。

### 19.1.3 Lチカ書き込み実績

`0.1.7-test8`の実機確認:

```text
FLASH: 444 B / 16 KB (2.71%)
RAM:     0 B / 2 KB  (0.00%)
VID:0x1209, PID:0xb803
Detected CH32V003
Image written.
Booting
```

基板上LEDの0.2秒点灯・0.8秒消灯を確認した。

`0.1.8-test9`では、`doctor`がNewlib依存なしと判定した一方、`01_macro_keyboard`の実コンパイル行に`-I/usr/include/newlib`が残っていた。このPASS判定は検査漏れであり、訂正する。

`0.1.9-test10`では、`ch32fun.mk`由来の`-I$(NEWLIB)`を除去し、必須演習3本の`make -n build`へ`/usr/include/newlib`が現れないことを`doctor`で確認する。test10の初版`doctor`は未使用の`NEWLIB?=/usr/include/newlib`既定値まで検出してFAILにしたため、test10aで実効オプションとdry-runを検査する方式へ修正した。文字列検索だけで合格にせず、実際に各演習Makefileが生成するコマンド列を検査する。test11／test12の演習02実コンパイル行でも`-I/usr/include/newlib`がないことを確認した。

## 20. ビルド再現性

リリース時には、少なくとも次を固定または記録する。

- UIAP Devkitバージョン
- クロスコンパイラのバージョン
- makeのバージョン
- 書き込みツールのバージョンまたはコミット
- Pythonのバージョン
- hidapiのバージョン
- `ch32fun`のコミット
- `rv003usb`のコミット
- ビルドオプション
- 対象MCU
- ボードバージョン
- ブートローダーVID:PID
- アプリケーションVID:PID
- USBシリアル番号生成方式
- ホストアプリ設定
- 入力部品とGPIO割り当て

## 21. 検証状態の記録

技術項目は、次の状態を区別して`70_VALIDATION_RESULTS.md`へ記録する。

- 提案
- 実装済み・未ビルド
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

## 22. エラーコードとメッセージ

参加者向けエラーは、原則として日本語で表示し、次を含む。エラーコード、コマンド名、VID:PIDなどの技術識別子は変更しない。

- 一意のエラーコード
- 何が失敗したか
- どの段階で失敗したか
- 次に実行するコマンド
- 参照する文書
- OS固有差異
- 演習を継続するための代替手段

確認済み例:

```text
UIAP-E103  Devkit展開先パス非対応
UIAP-E202  Devkit内GNU Make未導入
UIAP-E207  hidapi import失敗
UIAP-E208  hidapi診断スクリプト失敗
UIAP-E299  doctorがリリース阻害項目を検出
UIAP-E311  Windowsパス互換性検査失敗
UIAP-F205  物理ブートローダー複数検出
UIAP-W203  macOS arm64版minichlink未導入
UIAP-W207  Devkit内Pythonまたはhidapi未導入
UIAP-E224  minichlinkに隔離属性が残存
UIAP-E225  minichlinkコード署名検証失敗
```

同じコードの意味をリリース間で変更しない。

## 23. ch32fun参加者向けサブセット

参加者向け`workspace/deps/ch32fun`は、固定済み上流コミットから許可リスト方式で生成する。

要件:

- 完全な上流ツリーへ対して削除処理を繰り返す方式を標準にしない
- 新しい空ディレクトリへ、許可リストの相対パスだけをコピーする
- 許可リスト外のファイルはデフォルト拒否とする
- 上流コミット、入力アーカイブSHA-256、ライセンス、ローカルパッチを固定する
- `LICENSE`、`SUBSET.md`、`UPSTREAM_COMMIT`、`ALLOWLIST.txt`を保持する
- `ch32fun/ch32fun.mk`、必要ヘッダー、リンカースクリプト、`minichlink`関連ファイルなどの必須パスを自動検査する
- 他MCU向けexamples、`projects`、`build_scripts`、PlatformIO設定を原則として配布しない
- 完全な上流ソース、許可リスト、生成スクリプト、パッチ、再生成手順を対応ソースへ含める
- 生成後サブセットで全採用演習をクリーンビルドし、完全版上流ツリーへ暗黙にフォールバックしていないことを確認する

Makefileは、サブセットでも完全版でも同じ公開パスを参照する。

```make
CH32FUN_ROOT ?= $(UIAP_WORKSPACE)/deps/ch32fun
CH32FUN ?= $(CH32FUN_ROOT)/ch32fun
```

演習Makefileから`examples`、`projects`、上流ルートのPlatformIO設定を参照しない。

詳細は`15_CH32FUN_SUBSET_RULES.md`を参照する。


## 24. `rv003usb`、書き込み変数、同梱Pythonで確認した規則

`workspace/exercises/03_pot_cursor_haptic`のWindows実機検証から、次を共通規則へ追加する。

### 24.1 `rv003usb`とSysTick

`rv003usb`を使用するCH32V003ファームウェアでは、`funconfig.h`に次を設定する。

```c
#define FUNCONF_SYSTICK_USE_HCLK 1
```

この設定を変更するとSysTickの周波数が変わるため、ミリ秒換算を固定値で記述しない。`FUNCONF_SYSTEM_CORE_CLOCK`と`FUNCONF_SYSTICK_USE_HCLK`から換算値を算出する。

### 24.2 `FLASH_COMMAND`と自動変数

Makeの`$<`、`$@`などの自動変数は、ターゲットのレシピ評価時に有効である。Makefile読込時に展開される`:=`へ直接入れない。

不採用例:

```make
FLASH_COMMAND := $(MINICHLINK)/minichlink -c 0x1209b803 -w $< flash -b
```

この例では`$<`が空になり、次のようなコマンドが生成される。

```text
minichlink -c 0x1209b803 -w  flash -b
```

確認済み例:

```make
FLASH_COMMAND = $(MINICHLINK)/minichlink -c 0x1209b803 -w $(TARGET).bin flash -b
```

`make flash`のログで、`-w`直後に実在する`.bin`ファイル名があることを確認する。

### 24.3 Windows Embedded Pythonのローカルimport

同梱のWindows Embedded Pythonでは、実行スクリプトのディレクトリがモジュール探索パスへ入らない構成がある。演習内`host`のローカルモジュールをimportするエントリーポイントは、自身のディレクトリを明示的に追加してよい。

```python
from pathlib import Path
import sys

HOST_DIR = Path(__file__).resolve().parent
if str(HOST_DIR) not in sys.path:
    sys.path.insert(0, str(HOST_DIR))
```

参加者に`PYTHONPATH`の手動設定、venvのactivate、システムPythonへの切替を要求しない。

### 24.4 Windows設定変更の単体テスト

HID入力とWindows設定変更を同時にデバッグしない。OS設定を変更する演習には、HIDを使用しない`make cursor-test`相当を用意する。設定変更前に起動時値を保存し、テスト終了時とエラー時に復元する。


## 25. Windows版Devkitルートの対応文字

Windows版Devkitは、ローカルドライブ上にあり、各フォルダー要素が次の文字だけで構成されたパスをサポートする。

```text
A-Z a-z 0-9 _ - .
```

複数階層を許可する。

有効な例:

```text
C:\uiap\uiap-devkit-win64
C:\pj\uiap-devkit-win64
C:\pj\xpfes2026\uiap-devkit-win64
```

非対応:

```text
C:\UIAP Test\uiap-devkit-win64
C:\開発\uiap-devkit-win64
\\server\share\uiap-devkit-win64
```

空白を含むパスを単に引用符で囲むだけでは、完全な対策にならない。現在の演習Makefileは、次のように外部Makefileを読み込む。

```make
include $(CH32FUN)/ch32fun.mk
```

GNU Makeの`include`では、展開後の空白がファイル名の区切りになる。さらに、`ch32fun.mk`が生成するソース、インクルード、リンカースクリプト、リダイレクト先の全引数を一貫してエスケープする必要がある。

全角文字は空白区切りとは別問題だが、Command Prompt、Windows PowerShell、GNU Make、xPack `sh.exe`、GCC間で文字コード処理の互換性を保証できない。このため、現行リリースでは非ASCIIパスを非対応とする。

### 25.1 判定処理の単一化

パス判定の正本は`scripts/path-check.ps1`とする。

- `start-uiap.cmd`は`path-check.ps1`を呼び出す
- `setup.ps1`は独自の正規表現を持たず、`path-check.ps1`を呼び出す
- `doctor.ps1`も同じ`path-check.ps1`を呼び出す
- エラーコードと日本語メッセージを共通化する
- 判定処理の単体テストを用意する

同じ正規表現を複数ファイルへコピーしない。

### 25.2 正規表現

正規表現を使用する場合の概念例:

```powershell
$asciiSafePattern = '^[A-Za-z]:\\[A-Za-z0-9._-]+(?:\\[A-Za-z0-9._-]+)*$'
```

このパターンは、ドライブ文字の後に1つ以上のフォルダー要素があり、同じ条件の要素が複数階層続くことを許可する。

Devkit `0.4.3-test11`で使用した次の形式は不正である。

```powershell
$asciiSafePattern = '^[A-Za-z]:\[A-Za-z0-9_.\-]+$'
```

問題:

- `\[`がWindowsの区切り文字ではなく、正規表現上のリテラル`[`として解釈される
- 複数階層を繰り返す構造がない
- 結果として有効な通常のWindowsパスまで拒否する

実装では、`[System.IO.Path]::GetFullPath()`による正規化、UNC判定、パス要素ごとの検査を分離することを推奨する。

### 25.3 必須テスト

最低限、次を自動テストする。

| 入力 | 期待結果 |
|---|---|
| `C:\uiap\uiap-devkit-win64` | 許可 |
| `C:\pj\uiap-devkit-win64` | 許可 |
| `C:\pj\xpfes2026\uiap-devkit-win64` | 許可 |
| `D:\work\xpfes2026\uiap-devkit-win64` | 許可 |
| `C:\UIAP Test\uiap-devkit-win64` | 拒否、`UIAP-E103` |
| `C:\開発\uiap-devkit-win64` | 拒否、`UIAP-E103` |
| `\\server\share\uiap-devkit-win64` | 拒否、`UIAP-E103` |

有効パスで`UIAP-E103`が出た場合は、参加者の展開ミスではなく、Devkitの回帰不具合として扱う。

### 25.4 メッセージ

実際に非対応パスである場合は次を行う。

1. `UIAP-E103`を表示
2. 原因、現在の場所、推奨移動先、再起動手順を日本語で表示
3. ダウンロード、展開、Make dry-runを開始しない

有効なパスを誤って拒否した場合は、フォルダー移動を案内しない。使用中Devkitのバージョンを確認し、修正版へ切り替える。

`subst`ドライブ、8.3短縮名、自動コピーを標準対策にしない。状態が残る、環境差がある、元のパスと表示パスが不一致になるため、初心者向け復旧が複雑になる。

## 26. macOS HID Boot KeyboardのDescriptorと制御要求

macOS向け`01_macro_keyboard`では、USB Device Descriptorのクラス3フィールドを次とする。

```text
bDeviceClass    = 0
bDeviceSubClass = 0
bDeviceProtocol = 0
```

HID Boot KeyboardはInterface Descriptorで宣言する。

```text
bInterfaceClass    = 0x03
bInterfaceSubClass = 0x01
bInterfaceProtocol = 0x01
```

ファームウェアは、少なくとも次のHIDクラス要求を処理する。

- `GET_REPORT`
- `GET_IDLE`
- `SET_IDLE`
- `GET_PROTOCOL`
- `SET_PROTOCOL`

未使用のLED Output ReportをReport Descriptorで宣言しない。宣言する場合は、対応するOutput Report処理も実装し、WindowsとmacOSで確認する。

`doctor`は、Device Descriptor、Interface Descriptor、`RV003USB_OTHER_CONTROL`、必要な要求処理シンボルを静的検査する。ただし静的検査のPASSだけでHID入力成功とは扱わず、USB Device列挙、IOHID列挙、キー入力、再接続を実機で別々に確認する。

## 27. macOSカーソル倍率APIのABI判定と復元

`02_rotary_cursor_size`のmacOSホストは、非公開の`CGSGetCursorScale`と`CGSSetCursorScale`を使用する検証実装である。公開APIではないため、関数宣言、引数型、値域、将来互換性を固定仕様として扱わない。

### 27.1 スカラーABI

第三者実装ではカーソル倍率の型に`float`と`CGFloat`の両方が見られる。Apple Siliconでは`CGFloat`が64bitであるため、32bit値を64bitとして読むと正常値を`0.00`相当へ誤読する可能性がある。

ホストは次を満たす。

- getterの書込み幅を安全なプローブ領域で確認する
- `float32`または`float64`として妥当な値だけを採用する
- getterで判定したABIと同じ型でsetterを呼び出す
- NaN、無限大、`0.00`、観測範囲外値を有効な現在値として扱わない
- `make host-doctor`で現在値の同値書込みと再読取りを行う
- 自己診断に失敗した場合は`make app`を開始しない

### 27.2 設定保存と復元

OS設定を変更する前に起動前値をDevkit内`.state`へ保存する。保存値は次を満たす場合だけ有効とする。

- 有限値
- 実機観測用の妥当範囲内
- 読取りAPIが成功している

変更後と復元後は再読取りし、許容誤差内で一致することを検証する。正常終了、設定変更エラー、HIDオープン失敗、USB切断時には復元を試行する。復元成功後は状態ファイルを削除する。

`Ctrl+C`終了時の復元はmacOS 26.5.2のtest12で利用者実機確認済みである。USB切断時復元は未確認のため、確認済みとして説明しない。

### 27.3 リリース判定

非公開APIを使用するため、少なくとも次をリリース候補ごとに確認する。

- `make host-doctor`
- `make app-dry-run`でCW／CCW
- `make app`で両方向のサイズ変更
- 上限・下限
- `Ctrl+C`終了時復元
- USB切断時復元
- 別ユーザー
- 対応する最低macOS
- 最新の対象macOS

公開APIだけで実現できる代替方式の検討は継続する。

## 28. Windowsオンラインダウンロード規約

### 28.1 標準実装

PowerShell補助スクリプトから、Windows標準の実行ファイルを明示する。

```powershell
$CurlPath = Join-Path $env:SystemRoot 'System32\curl.exe'
& $CurlPath @Arguments
```

`curl`だけを記述しない。Windows PowerShell 5.1では`curl`が`Invoke-WebRequest`の別名として解決される場合があり、curlオプションと互換にならない。

標準引数:

```text
--fail
--location
--retry 3
--retry-delay 2
--connect-timeout 30
--progress-bar
--output <archive>.part
```

未完了ファイルが存在する場合だけ次を追加する。

```text
--continue-at -
```

外部プログラムは文字列連結したコマンドとして実行せず、引数配列で実行する。curl終了コードを`$LASTEXITCODE`で取得し、PowerShellの成功状態だけで判定しない。

### 28.2 完了条件

1. curl終了コードが0
2. `.part`のSHA-256が固定値と一致
3. 正式なキャッシュ名へ同一ボリューム内で変更
4. 展開またはインストール処理が成功
5. コンポーネントSHA-256をインストールマーカーへ記録

SHA-256が一致する前に正式名へ変更しない。既存の正式キャッシュが不一致の場合は上書き再利用せず、`.bad-<timestamp>`へ隔離する。

### 28.3 再開と再試行

- curlの内部再試行は3回とする
- `.part`がある場合はRange再開を試みる
- curl終了コード33の場合は再開非対応として`.part`を削除し、1回だけ先頭から取得し直す
- その他の失敗では`.part`を保持し、利用者が`setup`を再実行できるようにする
- SHA-256不一致の`.part`は再開候補として残さない

### 28.4 ログ

curlの進捗メーターはコンソールへ直接表示し、ログファイルへリダイレクトしない。ログには次だけを残す。

- コンポーネント名
- URL
- 再開の有無
- curl終了コード
- SHA-256期待値と実測値
- キャッシュ採用、成功、失敗

URLにトークン、認証情報、個人情報を含めない。

## 29. Windows標準実行ファイルの呼出し

DevkitがPATHを再構成する処理では、Windows標準実行ファイルを相対名だけで呼び出さない。

```text
%SystemRoot%\System32\cmd.exe
%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe
%SystemRoot%\System32\curl.exe
```

Devkit内ツールはPATHの先頭へ置いてよいが、System32、Wbem、Windows PowerShellをPATHへ保持する。起動スクリプト、共通コマンドラッパー、PowerShellからの再呼出しで同じ規則を使用する。

## 30. 外部取得物の識別とSHA-256

SHA-256は、版やコミットだけでなく、実際に取得するファイルのバイト列へ結び付ける。同じソースコミットから生成されたZIP、tar.gz、その他のアーカイブは、展開内容が同等でも別の取得物として扱う。

固定ロックには、少なくとも次を含める。

- コンポーネント名と版またはコミット
- 取得URL
- 保存ファイル名
- アーカイブ形式
- SHA-256

URL、保存ファイル名、アーカイブ形式、SHA-256は相互に整合していなければならない。いずれかを変更した場合はロックを更新し、新しいDevkit版として再検証する。SHA-256不一致時に、取得した実測値だけを根拠として期待値を書き換えない。

ch32fun固有の入力値は`15_CH32FUN_SUBSET_RULES.md`、リリース判定は`50_RELEASE_CHECKLIST.md`、利用者向け復旧は`60_TROUBLESHOOTING.md`、実機結果は`70_VALIDATION_RESULTS.md`へ分離する。

## 2026-08-01 必須演習の実装完全性

参加者向けまたは主催者検証用Devkitに必須演習ディレクトリを含める場合、実装を停止するだけのプレースホルダーを含めない。

リリース検査では、少なくとも次を行う。

- `01_macro_keyboard`に主ソース、`usb_config.h`、Makefileが存在する
- `02_rotary_cursor_size`に主ソース、`usb_config.h`、ホストアプリ、Makefileが存在する
- 演習ツリーに`UIAP-E240`が残っていない
- 両Makefileが`$(UIAP_WORKSPACE)/deps/rv003usb`を参照する
- `make -n build`が3演習で成功する
- 実機結果を伴わない再実装は「静的検査済み」と「Windows実機確認済み」を分けて記録する

オンライン方式で固定コミットのRaw URLからソースを取得する場合、URLへ完全コミットIDを含め、取得した各ファイルのSHA-256を記録する。最終リリースでは、その実測値を期待値として固定し、取得後に必ず検証する。

## 2026-08-01 Make自動変数を含む書き込みコマンド

`$<`、`$@`などのGNU Make自動変数は、対象ルールのレシピ実行時にだけ値を持つ。自動変数を含むコマンド変数を単純展開代入`:=`で定義しない。

不適切な例:

```make
FLASH_COMMAND := "$(MINICHLINK)/minichlink" -c 0x1209b803 -w $< $(WRITE_SECTION) -b
```

`:=`の評価時点では`$<`が空になるため、`cv_flash`実行時に書き込みファイルが欠落する。

採用する形式:

```make
FLASH_COMMAND = "$(MINICHLINK)/minichlink" -c 0x1209b803 -w $< $(WRITE_SECTION) -b
```

または、対象ルールのレシピへ`$(TARGET).bin`を明示する。リリース検査では`make -n flash`を実行し、`-w`直後に対象BIN、その後に書き込み領域`flash`と`-b`が存在することを確認する。

Newlib依存の診断は、`NEWLIB?=/usr/include/newlib`のような未使用既定値の存在だけでFAILにしない。必須演習の`make -n build`に現れる実効コンパイル行を判定対象とする。実機事実は`70_VALIDATION_RESULTS.md`、復旧方法は`60_TROUBLESHOOTING.md`を参照する。

<!-- Source: 30_HARDWARE_RULES.md -->

# ハードウェア、回路、USBの設計規約

## 1. 前提

特に指定がない限り、対象は次とする。

- UIAPduino Pro Micro CH32V003 V1.4
- MCU: CH32V003
- PC接続: 主にUSB
- ワークショップ参加者: 電子工作初心者を含む

別のボードや部品を扱う場合は、差異を明示する。

## 2. 回路提案時の必須確認

回路や配線を提案するときは、少なくとも次を確認する。

- 使用GPIO
- GPIOの入出力方向
- 電源電圧
- 信号電圧
- GPIOの許容電流
- 負荷電流
- GNDの共通接続
- プルアップまたはプルダウン
- 逆起電力の有無
- 保護抵抗の必要性
- 逆接続の危険
- USB電源容量への影響
- 部品の定格
- 初心者が誤配線しやすい箇所

不明な定格を推測で断定しない。

## 3. GPIOへの直接接続

次の負荷をGPIOへ直接接続してよいと仮定しない。

- モーター
- リレー
- 大電流LED
- スピーカー
- ソレノイド
- 長いLEDテープ
- 容量性負荷
- 誘導性負荷

GPIOの出力電流、電圧降下、発熱、突入電流を確認する。

直接駆動できない場合は、MOSFET、トランジスタ、ドライバICなどを使用する。

## 4. モーターと誘導性負荷

振動モーターなどを扱う場合は、原則として次を検討する。

- ローサイドスイッチ
- ロジックレベルMOSFET
- ゲート抵抗
- ゲートプルダウン
- フライバックダイオード
- モーター電源のデカップリング
- MCU電源へのノイズ
- PWM周波数
- 起動電流
- 連続運転時の温度

回路図には、部品値、極性、GND、モーター電源を明示する。

ドライバー回路内蔵の5V振動モーターモジュールを使用する場合も、モジュールのVCC、GND、INを区別し、VCC-GND間へ100µF程度のバルクコンデンサーを近接配置する。GPIOはモーター本体ではなくIN端子だけを駆動する。

振動の知覚性を上げる場合は、定格を超える電圧へ上げるのではなく、ON時間とパルス回数を調整する。確認済みPoCでは、D6/A2（PC4）をHighにする80msパルス2回、間隔40msを強めの既定値とした。

## 5. LED

LEDをGPIOで駆動する場合は、電流制限抵抗を使用する。

テープLEDや複数LEDの場合は、総電流を計算し、USBまたは外部電源の容量を確認する。

アドレス指定LEDを扱う場合は、次も確認する。

- 信号電圧の互換性
- 電源投入順序
- データ線保護抵抗
- 大容量コンデンサ
- 最大輝度時の総電流

## 6. スイッチとエンコーダ

入力回路では、次を明示する。

- 内部プルアップまたは外部抵抗
- アクティブHigh/Low
- チャタリング対策
- サンプリング周期
- エンコーダのA/B相
- CW/CCW判定規則
- GND接続

初心者向け演習では、配線本数と状態確認方法を明確にする。

## 7. アナログ入力

ポテンショメーターやスライドボリュームを扱う場合は、次を確認する。

- ADC対応ピン
- 入力電圧範囲
- 電源電圧
- 両端とワイパーの接続
- 入力インピーダンス
- ノイズ
- 平滑化
- キャリブレーション
- 端点での期待値
- ADCチャンネル切替後のセトリング
- モーターなど出力負荷による電源ノイズ
- 段階変換時のヒステリシスと確定待ち

### 7.1 5V駆動ポテンショメーターの確認済みPoC構成

UIAPduinoのMCU電源より高い5Vをポテンショメーター両端へ接続する場合、ワイパーをADCへ直結しない。

確認済みの`03_pot_cursor_haptic`では、次の2系統を同じ抵抗比で分圧した。

- RV09 B10Kワイパー → 68kΩ直列、100kΩ対GND、0.1µF対GND → D1/A0（PA2/A0）
- +5V基準 → 68kΩ直列、100kΩ対GND、0.1µF対GND → D0/A1（PA1/A1）

ファームウェアは、ワイパーADC値と5V基準ADC値の比から0～1023へ正規化する。この方式はUSB 5Vの変動を比率計算で相殺するが、抵抗誤差、ADC入力インピーダンス、配線ノイズを無視しない。

確認済みの安定化処理:

- チャンネル切替後の読取り破棄
- 16回測定から最大値と最小値を除外した平均
- 5点中央値
- 低域フィルタ
- 報告値デッドバンド
- 段階境界ヒステリシス
- 連続サンプルによる段階確定
- モーター駆動中と停止後50msのADC更新停止

部品、配線、モーター個体が変わる場合は、静止時のADC幅と応答速度を再検証する。

## 8. USB

USB HIDなどを扱う場合は、少なくとも次を確認する。

- USB Low-SpeedまたはFull-Speedの前提
- エンドポイント数
- 最大パケットサイズ
- ポーリング間隔
- Report Descriptor
- Report IDの有無
- Usage Page
- Usage
- Input/Output/Feature Report
- OS標準ドライバで動作するか
- WindowsとmacOSでの認識差
- 複合デバイスにする必要性
- ブートローダーとの競合
- 書き込み時と通常動作時のUSB切り替え

HIDクラスを使う場合も、用途に適したUsageを選び、ホスト側挙動を実機で確認する。

## 9. USB HIDの検証

最低限、両OSで次を確認する。

- デバイスが列挙される
- Vendor ID/Product IDが想定どおり
- デバイス名が想定どおり
- Report Descriptorが解析できる
- 入力レポートが届く
- 出力レポートまたはFeature Reportが必要な場合は送受信できる
- 再接続後に復帰する
- 書き込み後に再列挙する
- 複数回の抜き差しで安定する
- スリープ復帰後に必要な動作をする

## 10. PCからデバイスを制御する場合

PCから振動ON/OFFなどを制御する場合は、候補を比較する。

- HID Output Report
- HID Feature Report
- Vendor-defined HID
- CDC
- 別USB-UART

ワークショップでは、OS標準ドライバで動作し、追加インストールが少ない方式を優先する。

ホスト側アプリが必要な場合は、WindowsとmacOSの両方で同じコードまたは同等手順を提供する。

## 11. 電源

次を必ず区別する。

- USB 5V
- MCUの動作電圧
- GPIO信号電圧
- 外部電源
- モーターやLEDの電源

USBポートから供給する総電流を見積もる。

外部電源を使用する場合は、GND共通化、逆流、電源投入順序を確認する。

## 12. 安全性

参加者向け回路では、次を優先する。

- 低電圧
- 低電流
- 発熱しにくい
- 極性ミスに気付きやすい
- ショートしにくい
- 部品点数が少ない
- 配線が視認しやすい
- 復旧しやすい

危険な電圧、商用電源、高温部品、過大電流を扱わない。

## 13. 部品提案

部品を提案するときは次を示す。

- 推奨部品
- 選定理由
- 必要定格
- 代替品
- 入手性
- パッケージ
- 初心者が扱いやすいか
- 追加部品
- 回路上の注意

型番だけでなく、最低限必要な電気的条件を示す。

## 14. 配線図と説明

配線説明には次を含める。

- UIAPduino側のピン名
- 部品側の端子名
- 電源
- GND
- 信号
- 抵抗値
- 極性
- 接続順序
- 動作確認方法

可能な場合は、表形式と回路図の両方を使う。

## 15. 段階的検証

複雑な演習は次の順に分割する。

1. 電源確認
2. 単純なGPIO出力
3. 単純なGPIO入力
4. 部品単体の動作
5. USB列挙
6. HID入力
7. HID出力またはPC制御
8. 演出や統合動作

各段階で成功条件を明示する。

## 16. 2026-07-31 必須演習の標準配線

必須演習の標準ハードウェア構成を次とする。

| 演習 | 配線 |
|---|---|
| `00_onboard_led_blink` | 外付け配線なし。基板上LEDを使用 |
| `01_macro_keyboard` | D5 / PC3とGNDの間にモメンタリスイッチ |
| `02_rotary_cursor_size` | D8 / PC6=A、GND=C、D9 / PC7=B |

`01_macro_keyboard`と`02_rotary_cursor_size`は内部プルアップを使用し、接点をGNDへ落とす。3端子ロータリーエンコーダーのC端子を3.3Vまたは5Vへ接続しない。配線変更前にはUSBを外す。

これらのGPIO割り当てを変更する場合は、ファームウェア、配線表、参加者向け手順、検証記録を同時に更新する。

<!-- Source: 40_WORKSHOP_GUIDE_RULES.md -->

# 参加者向け手順書の作成規約

更新日: 2026-08-01

## 1. 対象読者

参加者には、電子工作、組み込み開発、C言語、コマンド操作、USB HID、Pythonの初心者を含む。

説明は、経験者だけが理解できる省略を避ける。参加者が講師の個別支援なしでも、現在位置、次の操作、成功条件、復旧方法を判断できる粒度で記述する。

## 2. 文書の検証状態

手順書には、対象OSと検証状態を明記する。

例:

```text
Windows 11 x64: 実機確認済み
macOS Apple Silicon: 未確認
```

Windowsでの成功を根拠に、macOSでも確認済みと記載しない。

PoC、候補、参加者向け採用済みを区別する。詳細な実機結果は`70_VALIDATION_RESULTS.md`を参照する。

## 3. 各演習の基本構成

各演習は原則として次の順で記述する。

1. この演習で作るもの
2. 検証済みOSとDevkitバージョン
3. 所要時間
4. 使用するボードと部品
5. 完成時の動作
6. 安全上の注意
7. 配線
8. 開発環境の起動
9. 実行場所
10. ビルド
11. 書き込み
12. USB列挙またはホストアプリ起動
13. 動作確認
14. 成功判定
15. よくある問題
16. 元に戻す方法
17. 発展課題

PC側アプリケーションがある演習では、起動、終了、USB切断、OS設定復旧を独立した手順として記載する。

## 4. 各手順で明示する内容

- 作業の目的
- 対象OS
- 対象Devkitバージョン
- 実行場所
- 実行コマンド
- 期待される表示
- 期待されるUSB列挙
- 期待される物理動作
- 成功判定
- 失敗時の確認項目
- 次へ進む条件
- 演習を中止して復旧へ切り替える条件

「ビルド成功」「書き込み成功」「USB列挙成功」「HID送受信成功」「PC側処理成功」「物理動作成功」を別の確認段階として記載する。

## 5. コマンドの書き方

- プロンプト記号を含めない
- コピーして実行できる形にする
- 複数行の場合は実行順を明確にする
- 実行ディレクトリを直前に示す
- WindowsとmacOSで同じコマンドを優先
- OS差がある場合は共通手順を先に書く
- 危険なコマンドには目的と影響を明示
- 内部ツールの複雑な引数を参加者へ入力させない

推奨する記載順:

Windows Command Prompt:

```text
cd /d "%UIAP_WORKSPACE%\exercises\02_rotary_cursor_size"
make clean
make
make flash
make app
```

macOS:

```sh
cd "$UIAP_WORKSPACE/exercises/02_rotary_cursor_size"
make clean
make
make flash
make app
```

WindowsネイティブDevkitで`setup`などの起動コンソール専用コマンドを使用する場合は、そのDevkit版だけの操作であることを明記する。

`sample`、`macro`、`blink`、`cursorapp`、`cursorlist`、`cursorrestore`などの独自コマンドで演習移動や演習固有操作を隠さない。受講者が`cd`で演習へ移動し、その演習の`make`ターゲットを実行する手順にする。

## 6. 開発環境の起動

Windowsでは`start-uiap.cmd`、macOSでは`start-uiap.command`から起動する。

参加者へ次を行わせない。

- ZIP内からの直接実行
- 任意のCommand PromptやPowerShellからの直接ビルド
- ランタイムやシェル環境の選択
- venvのactivate
- 書き込みツールの直接実行
- ZadigまたはUSBドライバー変更
- 管理者権限が必要な操作

最終参加者向け版もオンライン・ブートストラップ方式とする。手順書には、ネットワークが必要な`setup`段階、固定済み取得物の検証、再実行方法を明記する。

### 6.1 演習の選択と移動

`start-uiap`起動後の現在位置は`workspace`とする。各演習の開始時に、対象フォルダーへの`cd`を必ず掲載する。

例:

```text
cd /d "%UIAP_WORKSPACE%\exercises\00_onboard_led_blink"
```

移動後、次で現在位置を確認できることを説明する。

Windows Command Prompt:

```text
cd
```

macOS:

```sh
pwd
```

演習名を隠す短縮コマンドは、初心者が現在位置を把握しにくく、演習READMEと実行対象がずれる原因になるため使用しない。

### 6.2 macOS Apple Siliconの初回起動

未署名・未公証の主催者検証版では、`start-uiap.command`の初回起動時にGatekeeperが停止する場合がある。参加者向け手順へ検証版を掲載する場合は、次を明記する。

1. 警告画面ではファイルを削除せず、画面を閉じる
2. 「システム設定」→「プライバシーとセキュリティ」を開く
3. 対象の`start-uiap.command`について個別に「このまま開く」を選ぶ
4. 再確認画面で起動を許可する

次を標準手順にしない。

- Gatekeeper全体の無効化
- `sudo spctl --master-disable`
- Devkit全体への無差別な`xattr -dr com.apple.quarantine`
- 管理者権限を使った回避

最終参加者向け版では、署名・公証するか、個別許可を正式手順として採用するかを決定し、実際にブラウザから取得したZIPで検証する。

2026-07-31までのmacOS 26.5.2実機検証では、個別許可後に主催者検証版を起動し、オンライン`setup`、`build-minichlink`、`build-host-tools`、`doctor`、必須演習3本を確認した。`02_rotary_cursor_size`はCW／CCW受信、カーソルサイズ変更、`Ctrl+C`終了時復元まで利用者実機確認済みである。別Mac、別ユーザー、macOS 26以降の追加環境、最終オンライン版の通しセットアップ、USB切断時復元は未確認である。

### 6.3 macOSのキーボード設定アシスタント

`01_macro_keyboard`を初めて接続したとき、macOSが「キーボード設定アシスタント」を表示する場合がある。今回のマクロデバイスには、アシスタントが要求する「左Shiftキーの右隣のキー」が存在しない。

参加者向け手順は次とする。

1. Mac本体のキーを代わりに押さない
2. 識別キーを求める画面から前の画面へ戻る
3. 1ページ目の「終了」を押して閉じる
4. テキストエディットなど安全な入力欄でスイッチを試す

macOS 26.5.2の実機では「スキップ」ボタンは表示されなかったため、「スキップしてANSIを選ぶ」を標準手順にしない。アシスタントを終了した後も`AbCdE`を入力でき、USB再接続時にはアシスタントは再表示されなかった。

画面表記がmacOSバージョンによって異なる場合も、存在しない物理キーをMac本体で代用しないことを優先する。参加者向けスクリーンショットには、対象macOSバージョンと「終了」ボタンの位置を明記する。

## 7. 配線説明

配線は表と図の両方を推奨する。

| UIAPduino | 部品 | 用途 |
|---|---|---|
| D5 / PC3 | モメンタリスイッチ | 内部プルアップ入力 |
| GND | モメンタリスイッチ | 押下時Low |

必要に応じて次も記載する。

- UIAPduino側のピン名とMCU端子名
- 部品側の端子名
- 電源電圧
- GND
- 信号
- 抵抗値
- 極性
- 部品の向き
- 使用しない端子
- 固定用タブと信号端子の区別
- 配線前にUSBを外すこと
- 配線後の目視確認
- 既存配線と競合しないこと

型番または製品ページを指定する場合は、汎用図ではなく、その製品の端子名と向きを使用する。

## 8. 検証済み入力例の記載

### モメンタリスイッチ

Windows実機PoCで確認した例:

```text
D5 / PC3 ─ モメンタリスイッチ ─ GND
```

- 内部プルアップ
- 押下時Low
- 押し続けでは繰り返さず、押下エッジで動作する構成を推奨
- チャタリング対策を明記

### 3端子ロータリーエンコーダー

Windows実機PoCで確認した例:

| UIAPduino | エンコーダー | 用途 |
|---|---|---|
| D8 / PC6 | A | A相、内部プルアップ |
| GND | C | 共通端子 |
| D9 / PC7 | B | B相、内部プルアップ |

注意:

- D5はモメンタリスイッチ用として使用し、エンコーダーでは使わない
- 3.3Vまたは5Vへ接続しない
- 固定用金属タブへ接続しない
- 軸側と端子側で左右が反転して見えることを説明
- 回転方向が逆の場合の対処を示す

部品型番と端子配置が一致していることを配布前に再確認する。


### RV09ポテンショメーター＋振動フィードバック

Windows 11 x64実機で確認した`03_pot_cursor_haptic`の例:

| UIAPduino | 接続先 | 用途 |
|---|---|---|
| +5V / GND | RV09の外側2端子 | ポテンショメーター電源 |
| D1/A0（PA2/A0） | ワイパーの68kΩ/100kΩ分圧 | 操作値ADC |
| D0/A1（PA1/A1） | +5Vの68kΩ/100kΩ分圧 | 5V基準ADC |
| D6/A2（PC4） | 振動モジュールIN | 振動制御 |
| +5V / GND | 振動モジュールVCC/GND | モーター電源 |

ADC2系統には0.1µF、モジュールVCC-GND間には100µFを配置する。5VワイパーをADCへ直結しない。

参加者向け手順は次の順序を推奨する。

```text
make clean
make flash
make doctor
make hidcheck
make adc-monitor
make cursor-test
make haptic-test HAPTIC_LEVEL=4
make app
```

各段階の成功条件を分ける。

- `make doctor`: ホスト側自己テストがPASS
- `make hidcheck`: `1209:D003`、Usage Page `0xFF00`、Usage `0x0001`を検出
- `make adc-monitor`: 静止時の値幅が小さく、段階が往復しない
- `make cursor-test`: `32 → 144 → 256`へ変化し、起動前設定へ復元
- `make haptic-test`: 選択したパターンを知覚できる
- `make app`: ポテンショメーター操作で15段階のサイズが変化し、変更成功時だけ振動する

アプリケーションVID:PID `1209:D003`、製品名、シリアル番号はPoC用一時値であることを記載する。

## 9. 成功条件

「成功したら何が起きるか」を具体的に書く。

悪い例:

```text
正しく動作します。
```

良い例:

```text
書き込み後、WindowsがHIDキーボードとして認識します。
メモ帳へ入力フォーカスを置き、スイッチを1回押すとAbCdEと入力されます。
```

ホストアプリを伴う例:

```text
make appを実行するとコンソールにCWまたはCCWが表示されます。
エンコーダーを1クリック回すたびに、Windowsのポインターサイズが1段階変化します。
```

上限、下限、1ステップの変化量も明記する。

## 10. HIDキーボード演習の安全

HIDキーボードは、フォーカスがあるアプリケーションへ実際にキー入力する。

手順書には次を明記する。

- メモ帳など安全な入力先を使用
- 日本語IMEをOFFまたは半角英数へ変更
- Caps Lockの状態を確認
- コマンドプロンプト、PowerShell、ブラウザのアドレス欄、パスワード欄へフォーカスを置かない
- 意図しない入力が続く場合はUSBケーブルを外す
- 再試行時はスイッチを一度完全に離す

期待文字列にShift修飾が含まれる場合は、OSやキーボード配列の影響を説明する。

## 11. PC側ホストアプリの手順

PC側Pythonプログラムは、対応する演習の`host`ディレクトリに置く。

```text
workspace/exercises/<exercise-name>/host/<program>.py
```

参加者向け手順では、最初に`cd`で演習ディレクトリへ移動させ、その場所から`make app`を実行させる。列挙は`make list`または`make hidcheck`、復元は`make restore`を使用する。参加者に`workspace/host`へ移動させたり、Pythonファイルの絶対パスを入力させたりしない。

PC側プログラムがない演習には、空の`host`ディレクトリを作成しない。`scripts/python`はDevkit全体の診断・復旧用であり、演習固有アプリの配置先として説明しない。

ホストアプリを使用する演習では、次を記載する。

1. 対象HIDデバイスの列挙確認
2. アプリ起動コマンド
3. 起動時に表示される製品名、VID:PID、Usage Page、Usage
4. 操作時のログ例
5. 終了方法
6. USB切断時の挙動
7. OS設定の復元方法
8. ログファイルの場所

終了方法:

```text
Ctrl+C
```

OS設定を変更するアプリでは、正常終了時に起動前の値へ戻すことを成功条件へ含める。

異常終了時の復元コマンド例:

```sh
make restore
```

自動再接続を行わない場合は、切断後に再接続してアプリを再起動する手順を明記する。

## 12. USB識別子の記載

ブートローダーVID:PIDとアプリケーションVID:PIDを分けて記載する。

```text
ブートローダー: 1209:B803
アプリケーション: 演習ごとの設定
```

PoCの一時値は、必ず一時値と明記する。

```text
1209:C003
1209:C004
1209:D003
TEST3-001
TEST7-001
```

これらを正式な公開配布用識別子として説明しない。

1台の物理USBデバイスが、Windows上で親デバイスと複数のHIDインターフェースとして表示されることがある。表示行数と物理ボード数を混同しない。

## 13. エラー説明

よくあるエラーには次を含める。

- エラーコード
- 実際に表示されるメッセージ
- 失敗した段階
- 主な原因
- 確認手順
- 修正手順
- 再実行するコマンド
- それでも直らない場合の切り分け
- 予備ボードや既知の正常演習へ切り替える条件

確認済み例:

- `UIAP-E207`: hidapi import失敗
- `UIAP-E208`: hidapi診断スクリプト失敗
- `UIAP-E311`: Windowsパス互換性検査失敗
- `UIAP-F205`: 物理ブートローダー複数検出

詳細は`60_TROUBLESHOOTING.md`へ分離する。

## 14. 初心者向け用語

専門用語は必要に応じて短く説明する。

- GPIO: マイコンの汎用入出力端子
- HID: キーボードやマウスなどで使われるUSBクラス
- Vendor-defined HID: 特定アプリと独自データを送受信するHID
- ビルド: ソースコードから書き込み用ファイルを作る処理
- フラッシュ: マイコンへプログラムを書き込む処理
- VID:PID: USBデバイスを識別する番号
- 再列挙: 書き込み後にUSBデバイスとして認識し直されること
- ホストアプリ: PC側でHIDデータを受信または送信するプログラム

用語説明が本文を圧迫する場合は用語集へ分離する。

## 15. 時間配分

1.5時間のワークショップでは、参加者全員が最低限の完成状態へ到達できる構成を優先する。

演習を次の3段階へ分ける。

- 必須: 全員が実施
- 追加: 早く終わった参加者向け
- 発展: ワークショップ後に試せる

必須演習は次の3本とする。

| 演習 | 最小到達点 |
|---|---|
| `00_onboard_led_blink` | ビルド、書き込み、基板上LED点滅 |
| `01_macro_keyboard` | スイッチ1回で`AbCdE`、長押し抑止、キー解放 |
| `02_rotary_cursor_size` | CW/CCW受信、カーソルサイズ変更、終了時復元 |

必須演習には、配線、ビルド、書き込み、USB列挙、最小動作確認だけを含める。

PC側アプリやパラメーター変更を含む場合も、完成済みサンプルを実行するだけで基本動作へ到達できる構成にする。`02_rotary_cursor_size`はmacOS 26.5.2の1台で基本動作を確認したが、非公開APIを使用するため、別Mac、最低対応macOS、USB切断時復元を確認するまでは十分な予備時間と代替デモを用意する。

## 16. 複数レベルへの対応

初心者向けには、変更箇所を限定する。

経験者向けの発展課題例:

- HID Report Descriptorの変更
- 入力数の追加
- 回転方向の反転
- 1クリックあたりの変化量変更
- デバウンス改善
- HID Output ReportまたはFeature Report
- 複数デバイス選択
- ログ形式の変更
- OS設定変更範囲の変更

発展課題が必須手順を妨げない構成にする。

## 17. スクリーンショットとログ

スクリーンショットを使う場合:

- 対象OSを明示
- 不要な個人情報を含めない
- 開発者固有のユーザー名を隠す
- USBデバイスの不要なシリアル番号を隠す
- 重要箇所が読める解像度
- UIの見た目だけに依存せず文章でも説明
- バージョン差で変わる画面は更新日を記録

コンソール例では、実在するユーザー名、ホームディレクトリ、MCU UUIDを削除または一般化する。

## 18. コード掲載

コード全体を掲載する必要がない場合は、変更箇所を明示する。

変更前後を示す場合は、次を示す。

- ファイル名
- 定数名または関数名
- 変更理由
- 期待される効果
- 元に戻す値

参加者がコピーするコードは、対象Devkit版で実際にビルドして確認済みのものを使用する。

## 19. 安全上の注意

必要な箇所で次を明示する。

- 配線変更前にUSBを外す
- 極性と端子名を確認する
- 金属部でショートさせない
- モーター、スピーカー、大電流LEDをGPIOへ直接接続しない
- 発熱、異臭、連続リセット時は直ちにUSBを外す
- 不明な状態で外部電源を接続しない
- HIDキーボード演習では安全な入力先を使用
- OS設定変更演習では復元方法を先に確認

## 20. 講師向け情報

参加者向け本文とは別に、講師用メモを用意する。

講師用メモには次を含める。

- 想定所要時間
- つまずきやすい箇所
- 検証済みDevkitバージョン
- 既知のエラーコード
- 予備UIAPduino
- 予備USBケーブル
- 交換用部品
- 配線済み見本
- 復旧用ファームウェア
- 代替PC
- OS設定復元コマンド
- 既知の正常な旧Devkit ZIP
- 先に進んだ参加者への発展課題

原因調査に時間がかかる場合は、問題の完全解決より演習継続を優先する。


## 21. Windows版の展開先案内

参加者向け事前案内では、ZIPの展開先を具体的に指定する。

推奨:

```text
C:\uiap\uiap-devkit-win64
```

代替:

```text
C:\pj\uiap-devkit-win64
C:\pj\xpfes2026\uiap-devkit-win64
```

複数階層でも、すべてのフォルダー名が半角英数字、ドット、ハイフン、アンダースコアだけで、空白を含まなければ利用できる。

次へ展開させない。

```text
デスクトップ
ドキュメント
OneDriveなどの同期対象
名前に空白を含むフォルダー
名前に日本語・全角文字を含むフォルダー
ネットワーク共有
```

### 21.1 `UIAP-E103`が表示された場合

最初に、表示された現在の場所を確認する。

実際に空白、全角文字、非ASCII文字、UNCパスが含まれている場合:

1. 表示中のコンソールを閉じる
2. `uiap-devkit-win64`フォルダー全体を推奨場所へ移動する
3. 移動先の`start-uiap.cmd`を実行する
4. `setup`を実行する
5. `doctor`がPASSになることを確認する

フォルダー移動後に古いコンソールを使い続けない。環境変数とPATHが移動前の場所を保持しているためである。

表示された場所が次のような有効なASCII・空白なしパスの場合は、移動を案内しない。

```text
C:\pj\xpfes2026\uiap-devkit-win64
```

この場合はDevkitのパス判定回帰を疑う。

- `VERSION`を確認する
- `0.4.3-test11`は使用しない
- 修正版Devkitへ切り替える
- 参加者にMakefile、PowerShell、正規表現を編集させない

参加者向けエラー本文は日本語で表示する。少なくとも、利用できない理由、現在の場所、推奨移動先、再起動手順を含める。

## 25. macOSでの書き込み手順の記述

macOS参加者向け手順では、ファームウェアのビルド成功とUSBブートローダー捕捉成功を分けて記載する。

標準手順:

```sh
cd "$UIAP_WORKSPACE/exercises/<exercise-name>"
make clean
make
```

書き込み前に、次を番号付きで示す。

1. UIAPduinoのRESETを押したままにする
2. データ通信対応USBケーブルを接続する
3. 約1秒待つ
4. RESETを離す
5. 直ちに`make flash`を実行する

成功確認は、コンソール表示と物理動作を分ける。

```text
Detected CH32V003
Image written.
Booting
```

Lチカでは、基板上LEDが0.2秒点灯・0.8秒消灯することを物理動作の成功条件とする。

次のエラーを混同しない。

- `Killed: 9`: macOS実行ポリシー、隔離属性、署名を主催者が確認する
- `Could not initialize b003boot programmer`: ブートローダーモード、RESET操作、USB接続、待機時間を確認する
- コンパイルエラー: ツールチェーン、依存ファイル、カレントディレクトリを確認する

参加者へDevkit全体の隔離属性削除、Gatekeeper全体の無効化、`codesign`の手動操作を要求しない。これらが必要な配布物は、当日用リリースとして不合格とする。

## 26. macOSロータリーカーソル演習の手順記載

対象Devkitは`uiap-devkit-macarm64` `0.2.1-test12`以降の検証済み版を明記する。

実行場所:

```sh
cd "$UIAP_WORKSPACE/exercises/02_rotary_cursor_size"
```

確認は次の順序に分ける。

```sh
make list
make app-dry-run
make host-doctor
make app
```

成功条件:

1. `make list`: `1209:C004`を1台検出する
2. `make app-dry-run`: カーソル設定を変えず、CWとCCWの両方を表示する
3. `make host-doctor`: カーソル倍率API、ABI判定、同値書込み、再読取りがPASSになる
4. `make app`: 回転方向に応じてカーソルサイズが変わる
5. `Ctrl+C`: 起動前のカーソルサイズへ戻る

`make host-doctor`で`current=0.00`、ABI不明、読取り失敗、同値書込み失敗が出た場合は`make app`へ進まない。

異常終了後の復元:

```sh
make restore
```

復元対象がない場合のエラーと、復元失敗を区別する。参加者向け資料には、非公開CoreGraphics APIを使用するためmacOS更新で動作が変わる可能性があること、動作しない場合は`make app-dry-run`までを成功扱いとして完成済みデモへ切り替えることを記載する。

## 20. オンライン検証版のダウンロード進捗説明

最終参加者向けオフライン版では大容量ダウンロードを手順に含めない。主催者検証版または事前セットアップ確認でオンライン`setup`を使用する場合だけ、次を明記する。

- 初回`setup`にはインターネット接続が必要
- `xPack GNU RISC-V Embedded GCC`などでは進捗バーが長時間表示される
- 表示が更新中であればコンソールを閉じない
- 中止は`Ctrl+C`
- 中止後は`.part`を手作業で削除せず、同じDevkitの`setup`を再実行する
- `SHA-256を検証しています`の表示後も完了メッセージまで待つ
- `[PASS] ダウンロードとSHA-256検証が完了しました`を取得成功条件とする
- `setup`成功と`doctor`成功を別段階として確認する

参加者へ`curl.exe`の長い引数を入力させない。操作は次へ限定する。

```text
setup
doctor
versions
```

進捗が表示されない、`UIAP-E121`、`UIAP-E122`、`.part`残留時の対処は`60_TROUBLESHOOTING.md`へ分離する。

## 21. Windows起動成功の確認

`start-uiap.cmd`をダブルクリックした後、案内が一瞬表示されるだけでは起動成功としない。成功条件は次とする。

- 案内表示後もウィンドウが閉じない
- 初期ディレクトリが`workspace`である
- `setup`、`doctor`、`versions`を入力できる
- `'cmd.exe' is not recognized...`が表示されない

起動シェルに失敗した場合は、PowerShellからの回避実行を参加者向け標準手順にせず、修正版Devkitへ交換する。

<!-- Source: 50_RELEASE_CHECKLIST.md -->

# 配布パッケージ作成・リリースチェックリスト

更新日: 2026-08-01

## 1. 対象成果物

- `uiap-devkit-win64.zip`
- `uiap-devkit-macarm64.zip`
- 対応ソースアーカイブ
- SBOM
- `SHA256SUMS`

検証用ZIPと最終参加者向けZIPを区別する。

最終参加者向け版もオンライン・ブートストラップ方式とする。検証用ZIPと最終ZIPは区別するが、取得方式自体は共通化する。

## 2. リリース元

配布版は、日常使用中の開発環境をそのまま圧縮して作らない。

クリーンな作業ディレクトリまたは自動化されたリリース手順から作成する。

入力となるバージョン、コミット、取得URL、SHA-256、パッチ、ライセンスを固定する。

## 3. 必須トップレベル項目

- `README.md`
- `VERSION`
- `manifest.sha256`
- 起動ファイル
- `runtime`
- `scripts`
- `workspace`
- `docs`
- `firmware`
- `licenses`

プロジェクト側では、次の文書を最新化する。

- `00_PROJECT_OVERVIEW.md`
- `10_DEVKIT_STRUCTURE.md`
- `15_CH32FUN_SUBSET_RULES.md`
- `20_BUILD_RULES.md`
- `40_WORKSHOP_GUIDE_RULES.md`
- `50_RELEASE_CHECKLIST.md`
- `60_TROUBLESHOOTING.md`
- `70_VALIDATION_RESULTS.md`
- `90_DECISIONS.md`
- `99_FULL_PROJECT_GUIDE.md`

`70_VALIDATION_RESULTS.md`を参加者向けZIPへ含めるかは別途判断する。少なくともリリース元リポジトリには保持する。

## 4. 配布版へ含めないもの

- 開発者個人のホーム
- セットアップ途中の一時ディレクトリ
- ダウンロードキャッシュ
- インストールログ
- ホストアプリの実行ログ
- クラッシュログ
- VS Code更新ログ
- パケットキャプチャ
- `cap.pcapng`
- 不要な`.git`
- バックアップファイル
- `*.bak`
- エディタ一時ファイル
- `.DS_Store`
- `Thumbs.db`
- `nul`
- 個人情報
- 開発者固有の絶対パス
- 実機のMCU UUID
- 未採用PoC
- 通常のビルド生成物
- 完成途中のvenv
- `.state`の個人別状態

生成物例:

```text
*.bin
*.elf
*.hex
*.lst
*.map
*_ext.bin
firmware.bin
```

復旧用など必要なバイナリは`firmware`へ整理し、対象、ビルド元、用途、SHA-256を記録する。
参加者向け`firmware`は、通常使用するものと講師の簡易復旧に必要なものへ限定する。SWIOなど専用機材を使う深い復旧用資材は参加者向けZIPと分離する。

## 5. Windows版ランタイム構成の確認

Windows版は、MSYS2を使用しないxPackベースのWindowsネイティブ構成とする。

- `runtime/msys64`が存在しない
- `start-uiap.cmd`、Makefile、文書がMSYS2またはUCRT64を参照しない
- xPack Windows Build Toolsが所定位置に存在
- xPack GNU RISC-V GCCが所定位置に存在
- Windows Command Promptから共通コマンドを実行できる
- PowerShell補助スクリプトがDevkit内パスだけで動作
- 同梱Pythonとhidapiが起動
- `python -c`に複雑な診断コードを埋め込んでいない
- Python診断コードが`.py`ファイルとして存在
- `scripts/cmd`の参加者向けコマンドがDevkit共通処理に限定されている
- `sample.cmd`、`macro.cmd`、`blink.cmd`、`cursorapp.cmd`、`cursorlist.cmd`、`cursorrestore.cmd`が存在しない
- `cursorstore`という誤記または別名がコマンド一覧に存在しない

### 共通

- `start-uiap.cmd`が固定パスを使っていない
- 管理者権限なしで起動
- 別ユーザーで起動
- 別ドライブへ展開して起動
- 日本語ロケールで起動
- Windows Defenderなどによる警告を確認
- ホスト側アプリが配布環境だけで起動
- Windows ARM64ではサポート外であることを明確に表示

## 6. macOS版固有確認

- macOS 26以降
- Apple Silicon arm64ネイティブ
- Rosetta 2不要
- Homebrew不要
- Xcode Command Line Tools不要
- 管理者権限不要
- `start-uiap.command`に実行権限
- `scripts/*.sh`に実行権限
- `runtime/bin/*`に実行権限
- ZIP展開後も権限保持
- ブラウザからダウンロードしたZIPで検証
- Gatekeeperの挙動を確認
- 不要な隔離属性削除を通常手順にしない
- 書き込みツールがUSBへアクセス可能
- ホスト側Pythonとhidapiがarm64ネイティブ
- minichlinkまたはdylibに`/opt/homebrew/`や`/Users/<開発者名>/`が残っていない
- Apple Silicon実機でビルド、書き込み、HID、ホストアプリを確認

### 6.1 2026-07-29主催者検証版の状態

`uiap-devkit-macarm64` `0.1.7-test8`について、macOS 26.5.2のApple Silicon実機で次を確認済みとする。

- `start-uiap.command`起動
- arm64ネイティブ、Rosetta不使用
- Devkitルートと初期`workspace`の解決
- オンライン`setup`
- GNU Make 4.4.1 arm64
- xPack RISC-V GCC 14.2.0-3 arm64
- 固定コミットの`ch32fun`、`rv003usb`
- libusb 1.0.29のarm64静的ビルド
- `build-minichlink`によるarm64版`minichlink`生成
- `minichlink`に開発者固有dylib依存がない
- `minichlink`の隔離属性なし
- `minichlink`のアドホック署名検証成功
- `doctor`結果`PASS=32 WARN=1 FAIL=1`
- Lチカファームウェアのビルド
- FLASH 444 B、RAM 0 B
- USBブートローダー`1209:B803`とCH32V003検出
- `make flash`、書き込み、ブート
- 基板上LEDの0.2秒点灯・0.8秒消灯

次は未合格であり、参加者向けリリースを阻害する。

- Devkit内Pythonとhidapi
- HID列挙・送受信とホストアプリ
- 最終許可リスト版`ch32fun`
- `ch32fun`とlibusb入力SHA-256の正式固定
- `-I/usr/include/newlib`への暗黙依存除去
- 最終オンライン`setup`の通し検証
- 別のApple Silicon Mac、別ユーザー、macOS 26以降の対象環境
- Developer ID署名・公証または正式な個別許可方針

`doctor`が`UIAP-E299`を返す間は、リリース候補として合格にしない。

### 6.2 minichlink配布前検査

- `file runtime/bin/minichlink`がMach-O arm64を示す
- `otool -L`の先頭行を依存関係として誤検出しない
- 動的libusbへ依存しない
- `/opt/homebrew/`、`/usr/local/`、`/Users/<developer>/`を含むdylib依存がない
- `xattr -p com.apple.quarantine runtime/bin/minichlink`が属性なしで終了する
- `codesign --verify --verbose=4 runtime/bin/minichlink`が成功する
- `minichlink.build-info`にソースコミット、libusbバージョン、入力SHA-256、成果物SHA-256がある
- 署名後に`strip`やバイナリ編集をしていない
- 主催者用`runtime/build`とダウンロードキャッシュを参加者向けZIPへ含めない
- Devkit全体への再帰的な隔離属性削除をリリース手順に含めない

### 6.3 2026-07-31 test9～test12の状態

`0.1.8-test9`では、次を確認した。

- `doctor`: `PASS=53 WARN=3 FAIL=0`
- `00_onboard_led_blink`: macOS実機合格
- `01_macro_keyboard`: ビルドと書き込みは成功
- USB Device `1209:C003`は`ioreg`で列挙
- Device Descriptorは`bDeviceClass = 3`
- `hidutil list`には現れず、macOSでは文字入力不可
- 同じ書き込み済みデバイスをWindowsへ接続すると`AbCdE`入力成功
- `doctor`がNewlib依存なしと判定した一方、実コンパイル行には`-I/usr/include/newlib`が残った

`0.1.9-test10`では、マクロキーボードのDevice Descriptor、HIDクラス要求、Newlibオプションを修正した。macOS 26.5.2実機でLチカと`AbCdE`入力、長押し抑止、再押下、キー解放、USB再接続を確認した。

test10の初版`doctor`は未使用の`NEWLIB?=/usr/include/newlib`既定値まで検出したため、`0.1.9-test10a`で実効`-I$(NEWLIB)`と必須演習dry-runだけを判定対象に修正した。

`0.2.0-test11`では、演習02のDevice DescriptorとHID制御要求を修正し、次を確認した。

- `1209:C004`、製品名、シリアル番号のIOHID列挙
- `make app-dry-run`でCW／CCW受信
- 実コンパイル行に`-I/usr/include/newlib`がない

一方、非公開カーソルAPIのスカラーABI不一致により、現在値を`0.00`と誤読し、`make app`は`UIAP-CURSOR-E207`、復元は`UIAP-CURSOR-E205`で失敗した。test11はカーソル変更機能のリリース候補として使用しない。

`0.2.1-test12`では、`float32`／`float64` ABIの実行時判定、不正値の保存防止、同値書込み自己診断、変更後・復元後の再読取り検証を追加した。macOS 26.5.2の利用者実機で次を確認した。

- 演習02のビルド、書き込み
- USB・IOHID列挙
- CW／CCW受信
- カーソルサイズ変更
- `Ctrl+C`終了時の起動前サイズ復元

次は引き続きリリース阻害項目である。

- USB切断時復元
- 最終レビュー済み`ch32fun`許可リスト
- `rv003usb`入力SHA-256の正式固定
- 最終オンライン`setup`の通し検証
- 別のApple Silicon Mac、別ユーザー、macOS 26以降の対象環境
- Developer ID署名・公証または正式な個別許可方針

## 7. 共通起動・セットアップ確認

1. ZIPをブラウザ相当の方法で取得
2. ZIPファイルのSHA-256を確認
3. 新しい場所へ完全に展開
4. ZIP内から直接実行していないことを確認
5. 開発環境を起動
6. セットアップ状態を表示
7. `doctor`または対応スクリプトを実行
8. `versions`または対応スクリプトを実行
9. セットアップを再実行して冪等性を確認
10. コンソールを閉じる
11. 起動ファイルから再度開く
12. PATHと環境変数が再設定される
13. 以前のコンソール状態へ依存せず動作
14. `workspace`から受講者が`cd`で各演習へ移動できる
15. `sample`、`macro`、`cursorapp`などを使わずに全演習手順を実行できる
16. 各演習の`make app`、`make list`、`make restore`などがグローバル別名なしで動作する

最終版を含むオンライン・ブートストラップ方式では、ダウンロード失敗、SHA-256不一致、途中再実行、正常キャッシュ再利用、固定URL以外へフォールバックしないことを確認する。

## 8. ビルド確認

次の必須演習について実行する。

```text
00_onboard_led_blink
01_macro_keyboard
02_rotary_cursor_size
```

各演習で次を実行する。

```text
make clean
make
make size
```

確認項目:

- `TARGET`と主ソース名が一致
- `CH32FUN`と`RV003USB`が`UIAP_WORKSPACE`基準
- Windowsで`sh`へ渡るパスが`C:/...`形式
- `C:pj...`のように区切りが消えていない
- `generated__.ld`を生成できる
- FLASHとRAMの使用量が表示される
- `rv003usb.S`の既知警告と実エラーを区別
- 通常生成物がリリースZIPへ混入していない

`doctor`またはCIで`make -n`によるパス互換性検査を実施する。

## 9. UIAPduino V1.4書き込み確認

Windows 11 x64で次を確認する。

- `make flash`がブートローダー`1209:B803`を使用
- `minichlink`実行時に`-c 0x1209b803`相当を指定
- 意図しない`1209:B003`参照が残っていない
- 現在接続中の物理USB親デバイスだけを数える
- HID子デバイスを別の物理ボードとして数えない
- 物理ブートローダーが0台の場合は待機または案内
- 物理ブートローダーが1台の場合だけ書き込み
- 2台以上の場合はインスタンスIDを表示して中止
- 成功時に`Detected CH32V003`、`Image written.`、`Booting`を確認
- 書き込み後に期待アプリケーションの再列挙を確認
- 外付け回路を外したフォールバック手順を確認
- 予備ボードへの交換手順を確認

macOS版は、採用する実際の書き込みツールと手順で別途実機検証する。

## 10. USB Descriptorとホスト側の整合性

USB HIDを含む場合、次を同一リリース内で一致させる。

- ファームウェアのVID:PID
- ホスト側ソースのVID:PID
- USB列挙スクリプトのVID:PID
- READMEのVID:PID
- Report ID
- レポート種別
- レポート長
- Usage PageとUsage
- 製品名
- USBシリアル番号の扱い
- デバイス役割

PoC用一時値を検索する。

```text
1209:C003
1209:C004
1209:D003
TEST3-001
TEST7-001
```

確認事項:

- 一時値であることが明記
- 正式値へ変更する箇所が特定済み
- 公開配布へそのまま使用しない
- MCU UUIDなど実機固有値がログや文書へ不要に残っていない

## 11. HIDマクロキーボード演習確認

確認項目:

- モメンタリスイッチがD5 / PC3とGNDの間
- 内部プルアップ
- 押下時Low
- デバウンスが有効
- キー押下レポート後に解放レポートを送信
- Device Descriptorのクラス3フィールドが`0`
- Interface DescriptorでHID Boot Keyboardを宣言
- `GET_REPORT`、`GET_IDLE`、`SET_IDLE`、`GET_PROTOCOL`、`SET_PROTOCOL`へ対応
- WindowsとmacOSがHIDキーボードとして列挙
- 安全な入力先で期待文字列を入力
- macOSの初回キーボード設定アシスタントは、存在しない識別キーを押さず、前の画面へ戻って「終了」で閉じる手順がある
- 「スキップ」ボタンが必ず存在すると仮定しない
- 日本語IMEとCaps Lockの注意がREADMEにある
- 意図しない連続入力時のUSB切断手順がある
- コマンドプロンプトやパスワード欄で試さない注意がある

PoCの期待文字列を変更した場合は、ファームウェア、README、検証記録を同時に更新する。

## 12. ロータリーエンコーダー＋ホストアプリ演習確認

検証済み3端子構成を使用する場合:

| UIAPduino | エンコーダー |
|---|---|
| D8 / PC6 | A |
| GND | C |
| D9 / PC7 | B |

確認項目:

- D5を使用していない
- 3.3Vまたは5Vへ接続していない
- 固定用タブへ接続していない
- A/C/Bの向きが部品図と一致
- 内部プルアップ
- CWとCCWを区別
- 1クリックあたりのカウント数が部品に一致
- 方向反転手順がある
- `--dry-run`相当でHIDイベントだけ確認可能
- ホストアプリが対象Usage Page、Usage、製品名を確認
- ポインターサイズが段階的に変化
- 上限と下限で範囲外へ進まない
- `Ctrl+C`で終了
- 正常終了時に起動前サイズへ復元
- `make restore`など異常終了後の復元手段がある
- USB切断時に明確なエラーで終了
- ログを`logs/`へ保存
- リリースZIPに実行ログが残っていない

## 13. ホスト側Pythonとhidapi

### 配置

- PC側Pythonプログラムが`workspace/exercises/<exercise-name>/host/`にある
- トップレベルの`workspace/host`が存在しない
- PC側プログラムがない演習に空の`host`がない
- 各演習の`make app`が同じ演習の`host`だけを参照する
- 別演習の`host`や開発者固有の絶対パスを参照しない
- Devkit共通の診断・復旧プログラムだけが`scripts/python`にある
- 旧パス`workspace/host`への参照がMakefile、README、スクリプト、文書に残っていない。ただし移行履歴とトラブルシューティングの旧パス説明を除く

確認項目:

- 同梱Pythonのバージョンが記録済み
- hidapi wheelのABIとアーキテクチャが一致
- `doctor`で`import hid`が成功
- 診断は`.py`ファイルを実行
- システムPythonへ依存しない
- venvを配布済み完成状態で含めない方針の場合、オフライン生成できる
- venvのactivateを参加者へ要求しない
- ホストアプリはフォアグラウンドで動作
- サービス、LaunchAgent、ログイン項目を作成しない
- 管理者権限を要求しない
- 切断時と設定変更失敗時を区別して表示

## 14. 展開場所依存の確認

少なくとも次で動作を確認する。

Windows:

```text
C:\uiap\uiap-devkit-win64
C:\pj\uiap-devkit-win64
```

macOS:

```text
~/uiap/uiap-devkit-macarm64
```

可能であれば別ドライブでも確認する。

固定パス検索対象:

- 開発者ユーザー名
- `C:\Users\`
- `/Users/`
- `C:\pj\`
- `/opt/homebrew/`
- 旧ディレクトリ`workspace/ch32fun`
- 旧ディレクトリ`workspace/rv003usb`
- `../ch32fun`
- `../rv003usb`
- `1209:B003`

意図した説明文や検査パターンを除き、実行パスとして残っていないことを確認する。

## 15. ディレクトリと不要物確認

- 外部依存が`workspace/deps`
- 参加者向け演習が`workspace/exercises`
- 演習固有のPC側プログラムが各演習の`host`配下
- トップレベルの`workspace/host`が存在しない
- 主催者用PoCが`workspace/poc`
- `workspace`直下に未移行の`*_poc`がない
- 採用済み演習と未採用PoCが混在しない
- 不要な`.git`がない
- `logs/`に実行ログがない
- `.state/`に個人状態がない
- `runtime/venv/`が配布方針と一致
- ビルド生成物がない
- Windows予約名がない
- シンボリックリンクへ依存しない

## 16. オフライン動作確認

ネットワークを切断し、次を確認する。

- Devkit起動
- 初期化またはvenv生成
- ビルド
- 書き込み
- HID列挙
- ホストアプリ起動
- HID送受信
- OS設定変更と復元
- 演習資料の参照
- 診断レポート生成
- 復旧手順

参加者向け標準手順に次を含めない。

- `pacman -S`
- Homebrew
- Git clone
- `pip install`による外部取得
- 外部サイトからの実行ファイル取得

オンライン・ブートストラップ方式そのものを最終方式とする。最終版では、検証用ロックではなくリリース用ロック情報で通し検証する。

## 16.1 演習移動コマンドの不在確認

参加者向けZIPと文書を検索する。

禁止するトップレベルコマンドまたはファイル:

```text
sample
macro
blink
cursorapp
cursorlist
cursorrestore
cursorstore
sample.cmd
macro.cmd
blink.cmd
cursorapp.cmd
cursorlist.cmd
cursorrestore.cmd
```

歴史的な検証記録または「廃止した名称」の説明を除き、参加者向け手順、`welcome.cmd`、トップレベルREADME、PATH上の実行ファイルに残っていないことを確認する。

演習別に次を実行する。

```text
cd /d "%UIAP_WORKSPACE%\exercises\<exercise-name>"
make help
```

演習に必要な操作がMakefileターゲットとして表示されることを確認する。

## 17. バージョンと依存関係

`VERSION`に記載する。

- UIAP Devkit名
- バージョン
- Platform
- Build-Date
- Online BootstrapまたはOffline Packageの区分

`workspace/deps/VERSIONS.md`に記録する。

- `ch32fun`
- `rv003usb`
- クロスコンパイラ
- make
- 書き込みツール
- Python
- hidapi
- ホスト側ツール
- ローカルパッチ
- 動作確認OS

## 18. チェックサムと完全性

`manifest.sha256`の対象:

- コンパイラ
- make
- 書き込みツール
- Python
- hidapi
- 起動ファイル
- 共通スクリプト
- ホストアプリ
- 復旧用ファームウェア
- 演習用ソース
- USB設定
- 重要文書

確認:

- 内部`manifest.sha256`が一致
- ZIPファイル自体のSHA-256を公開
- 対応ソース、SBOM、ZIPを`SHA256SUMS`へ記載
- SHA-256検証手順がREADMEにある

## 19. ライセンスと対応ソース

次を確認する。

- バイナリ再配布可否
- 著作権表示
- ライセンス本文
- ソース提供義務
- 変更表示義務
- GCC Runtime Library Exception
- GNU Make
- xPack Windows Build Tools
- Pythonと第三者ライセンス
- hidapi
- libusbを同梱する場合のLGPL対応
- `ch32fun`
- `rv003usb`
- minichlink
- 主催者作成コード

不足がある場合はリリースしない。

対応ソースには、正確な上流ソース、パッチ、ビルド手順、サブセット生成手順を含める。

## 20. 文書整合性

- `90_DECISIONS.md`が最新
- `70_VALIDATION_RESULTS.md`が最新
- 分野別文書が最新決定と矛盾しない
- PoC READMEの検証状態が実際の結果と一致
- Windows確認済みとmacOS未確認を混同していない
- 検証版と最終版のロック情報・バージョンを混同していない
- PoC用識別子を正式値として扱っていない
- `60_TROUBLESHOOTING.md`に既知問題が反映済み
- `99_FULL_PROJECT_GUIDE.md`を分割文書から再生成
- コマンドにプロンプト記号がない
- スクリーンショットとログに個人情報がない

## 21. 参加者環境での確認

開発に使用したPC以外で確認する。

最低限:

- 別のWindows 11 x64 PC
- 別のmacOS 26以降Apple Silicon端末
- 管理者権限のないユーザー
- 日本語ロケール
- 通常ネットワークでの初回`setup`
- ダウンロード失敗時の明確なエラーと再実行
- 別USBポート
- PC直結
- 許容するUSBハブ
- 異なる展開先

## 22. 検証結果の記録

各リリース候補の結果を`70_VALIDATION_RESULTS.md`へ記録する。

最低限:

- 日付
- OS
- Devkitバージョン
- 対象ボード
- 使用部品
- 配線
- 依存バージョン
- 実行コマンド
- FLASH/RAM使用量
- ブートローダーVID:PID
- アプリケーションVID:PID
- USBシリアル番号
- HID方式
- 成功した段階
- 発生した問題
- 修正内容
- 未確認事項

実機UUID、個人パス、不要なUSBシリアル番号は記録しない。

## 23. ワークショップ前の最終確認

- 配布URLが有効
- SHA-256が一致
- READMEの手順が最新
- 事前診断手順が最新
- テキストエディターの事前準備案内がある
- USBケーブル要件が明記
- UIAPduinoの台数が足りる
- 予備ボードが十分
- 予備ケーブルがある
- 予備部品がある
- 復旧用ファームウェアがある
- 講師用の既知問題一覧がある
- 配線済み見本がある
- 完成済みデモがある
- OS設定復元方法を講師が確認済み
- HIDキーボード演習の安全な入力先を用意
- 外部負荷は電源投入直後に安全状態
- 当日のネットワーク利用方針、事前`setup`完了条件、障害時の代替手順を確認

## 24. ch32fun許可リストサブセット確認

参加者向け`workspace/deps/ch32fun`について、次を確認する。

### 入力と来歴

- 上流リポジトリと固定コミットが記録されている
- 入力アーカイブまたは保存済み完全版ソースのSHA-256が固定されている
- 入力SHA-256不一致時に生成を中止する
- ローカルパッチが個別ファイルとして保存されている
- サブセット生成スクリプトと検査スクリプトがソース管理されている

### 許可リスト

- 新しい空ディレクトリへ許可ファイルだけをコピーする
- 許可リストのパスが相対パスである
- `..`、絶対パス、ドライブ文字、上流ルート外参照を拒否する
- 同じ入力と許可リストから再生成したファイル一覧とハッシュが一致する
- 必須パス一覧と禁止パス一覧を別途検査する

### 参加者向けツリー

- `LICENSE`が存在する
- `SUBSET.md`が存在する
- `UPSTREAM_COMMIT`が固定コミットと一致する
- `ALLOWLIST.txt`が実際の生成規則と一致する
- `ch32fun/ch32fun.mk`、必要ヘッダー、リンカースクリプトが存在する
- 配布する書き込みツールに必要な`minichlink`関連ファイルが存在する
- 使用する場合は`misc/libgcc.a`が存在する
- 採用演習が参照する`extralibs`だけが存在する

### 禁止領域

次が存在しないことを確認する。

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

例外を追加する場合は、ファイル単位で理由、使用演習、ライセンス、検証結果を記録する。

### 動作確認

- Windows 11 x64で全採用演習を`make clean`、`make`、`make size`、`make flash`
- macOS Apple Siliconで同じ確認
- USB列挙、HID送受信、ホストアプリ、設定復元
- 最終オンライン`setup`で生成された依存だけを使用
- 完全版上流ツリーが同じPCの別位置に存在しない状態
- `make -n`、ログ、依存ファイルに除外パスへの参照がない

## 25. ch32fun対応ソースとSBOM

- 対応ソースに完全な固定コミットの上流ソースを含める
- 許可リスト、生成スクリプト、検査スクリプト、ローカルパッチを含める
- サブセット再生成手順を含める
- 上流MIT `LICENSE`を保持する
- SBOMに配布形態`subset`、上流コミット、入力SHA-256、生成規則バージョンを記載する
- 参加者向けZIP、対応ソースアーカイブ、SBOMを`SHA256SUMS`へ記載する
- 参加者向けZIPのSBOMが、完全版上流ツリーを配布済みと誤記していない


## 26. `03_pot_cursor_haptic`リリース候補確認

対象リビジョン: `v1.0.8`

### 配置と内容

- `workspace/exercises/03_pot_cursor_haptic`へ配置
- ファームウェア、Makefile、README、`docs/WIRING.md`、`docs/VALIDATION.md`が存在
- ホストプログラムと補助モジュールが同じ演習の`host`配下に存在
- トップレベル`workspace/host`を参照しない
- `manifest.sha256`が一致
- `.elf`、`.bin`、`.hex`、`.lst`、`.map`、ログ、stateを配布ZIPへ含めない

### ビルドと書き込み

- `FUNCONF_SYSTICK_USE_HCLK`が1
- SysTick時間換算がクロック設定から計算される
- `make clean`、`make`、`make size`が成功
- 確認値: FLASH 3428 B、RAM 252 B
- 書き込みコマンドの`-w`直後が`pot_cursor_haptic.bin`
- ブートローダー`1209:B803`から書き込み成功
- `shasum: not found`警告と実際の書き込み失敗を区別

### HIDとホストアプリ

- `make doctor`がPASS
- `make hidcheck`で`1209:D003`、Usage Page `0xFF00`、Usage `0x0001`を確認
- Windows Embedded Pythonで演習内ローカルモジュールをimportできる
- `make cursor-test`でポインターサイズが即時変化し、起動前設定へ復元
- `make haptic-test HAPTIC_LEVEL=4`で80ms×2、間隔40msを確認
- `make app`でADC値、15段階、ポインターサイズ、振動が連動
- stale stateを検出した場合、アプリ起動前に復元

### ADC安定性

- `make adc-monitor`で静止時のmin/max/spanを確認
- v1.0.8の外れ値除去、中央値、低域フィルタ、デッドバンドが有効
- 段階ヒステリシスと3サンプル確定待ちが有効
- モーター駆動中と停止後50msはADC更新を行わない
- 境界付近でポインターサイズが往復しないことを実機確認

### リリース判定上の制限

- Windows 11 x64 PoCとして確認済み
- 正式VID:PIDとUSBシリアル番号は未決定
- macOS相当ホスト処理は未実装
- USB切断時、強制終了時、スリープ復帰、複数個体、長時間動作は追加検証対象
- ワークショップ必須演習としての採用は未決定


## 27. Windows展開先パス検査

パス検査の正本が`scripts/path-check.ps1`へ集約されていることを確認する。

- `setup.ps1`と`doctor.ps1`に独立した判定正規表現がない
- `start-uiap.cmd`、`setup.ps1`、`doctor.ps1`が同じ終了コードと日本語メッセージを使用する
- 判定処理の自動テストがある

リリース候補を次のパターンで確認する。

| 展開先 | 期待結果 |
|---|---|
| `C:\uiap\uiap-devkit-win64` | 起動、`setup`、`doctor`へ進む |
| `C:\pj\uiap-devkit-win64` | 起動、`setup`、`doctor`へ進む |
| `C:\pj\xpfes2026\uiap-devkit-win64` | 起動、`setup`、`doctor`へ進む |
| `D:\work\xpfes2026\uiap-devkit-win64` | 起動、`setup`、`doctor`へ進む |
| `C:\UIAP Test\uiap-devkit-win64` | `UIAP-E103`でダウンロード前に停止 |
| `C:\開発\uiap-devkit-win64` | `UIAP-E103`でダウンロード前に停止 |
| `\\server\share\uiap-devkit-win64` | `UIAP-E103`でダウンロード前に停止 |

追加確認:

- 有効な複数階層ASCIIパスを拒否しない
- UNCパスを拒否する
- エラーに現在パスと推奨移動先が表示される
- 原因、現在の場所、推奨移動先、再起動手順が日本語で表示される
- 英語だけの説明が残っていない
- エラー後に`runtime/downloads`へ新しいファイルを作成しない
- 実際に非対応パスである場合、フォルダー移動後に新しい`start-uiap.cmd`から正常起動できる
- 古いコンソールを再利用しない案内がある
- `VERSION`とREADMEへ対応パスを記録する

### 回帰防止

次の誤った正規表現または同等の実装を検出した場合、リリースを中止する。

```powershell
'^[A-Za-z]:\[A-Za-z0-9_.\-]+$'
```

Devkit `0.4.3-test11`は、有効な`C:\pj\xpfes2026\uiap-devkit-win64`を拒否するため、リリース候補として使用しない。

有効パスで`UIAP-E103`が発生した場合、フォルダー移動で回避して合格扱いにしない。判定処理を修正し、全パターンを再検証する。

任意パス対応を合格条件にしない。現行方針では、有効なASCII・空白なし複数階層パスを許可し、非対応パスだけを早期かつ明確に拒否できることを合格条件とする。

## 17. Windowsダウンロード進捗機能の検査

オンライン初期化型Windows版では、次をすべて確認する。

### 固定情報

- `bootstrap.lock.json`の各SHA-256が64桁の16進数
- URL、版、ファイル名、SHA-256が公式配布情報と一致
- PowerShellの`curl`別名を使用していない
- `%SystemRoot%\System32\curl.exe`または`curl.exe`実体を使用する
- 認証トークンや個人用URLがない

### 正常系

- 大容量xPack GCCで進捗が更新される
- 進捗バーと完了割合が表示される
- HTTPリダイレクトを追跡できる
- 完了後にSHA-256を検証する
- 検証成功後だけ`.part`から正式名へ変更する
- 2回目の`setup`で検証済みキャッシュを再利用する
- 展開済みコンポーネントを不要に再展開しない

### 中断・復旧

- `Ctrl+C`中断後に`.part`が残る
- 再実行でRange再開を試みる
- 再開非対応時のcurl終了コード33で先頭から自動再取得する
- DNS失敗、接続失敗、タイムアウト、TLS失敗を別のcurl終了コードとして表示する
- 失敗時に正式キャッシュ名を作らない
- `.part`を利用者へ手動編集させない

### 完全性

- 正しい長さでSHA-256不一致のテストファイルを`.bad-*`へ隔離する
- 既存の正式キャッシュが不一致の場合も再利用しない
- SHA-256期待値をエラー回避目的で現場変更しない
- エラー修正後に同じ`setup`を再実行できる

### ログ

- 進捗バーの制御文字や同一行更新をログへ保存しない
- 開始、再開、終了コード、SHA-256、成功・失敗だけを記録する
- ログにユーザー名、不要な絶対パス、認証情報を含めない

`uiap-devkit-win64` `0.5.0-test13`は2026-08-01時点で静的検査のみであり、この節のWindows実機項目は未合格である。

## 18. Windows起動シェル検査

- `start-uiap.cmd`が`cmd.exe`を相対名だけで実行していない
- `start-uiap.cmd`と`scripts/cmd/*.cmd`がWindows PowerShellを相対名だけで実行していない
- `%SystemRoot%\System32\cmd.exe`が存在することを起動前に確認する
- `%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe`が存在することを確認する
- Devkit用PATHにSystem32、Wbem、Windows PowerShellが含まれる
- ダブルクリック後、案内表示から専用Command Promptの入力待ちへ移行する
- 起動失敗時は`pause`相当でメッセージを読める
- PowerShellから起動した場合だけ成功する状態を合格にしない

`0.5.1-test14`は相対名`cmd.exe`の解決に失敗したため、リリース候補として使用しない。

## 19. 取得アーカイブロックの整合性

オンライン取得物ごとに次を確認する。

- ロックにURL、保存ファイル名、アーカイブ形式、SHA-256がある
- URLと保存ファイル名の拡張子がアーカイブ形式と一致する
- SHA-256が、そのURLから取得する実ファイル全体の値である
- 同じコミットのZIPとtar.gzでSHA-256を共有していない
- `VERSION`とロック内のDevkit版が一致する
- ロック変更後に正常取得、キャッシュ再利用、不一致隔離を再検証した

ch32funの具体的な入力値は`15_CH32FUN_SUBSET_RULES.md`を参照し、このチェックリストへ重複記載しない。

## 2026-08-01 Windows test17追加検査

`uiap-devkit-win64` `0.6.0-test17`では、次を確認する。

- [ ] `VERSION`と`bootstrap.lock.json`が`0.6.0-test17`で一致
- [ ] `01_macro_keyboard`のプレースホルダーがなく、必要ソースが揃っている
- [ ] `02_rotary_cursor_size`のプレースホルダーがなく、ホストアプリを演習内`host`へ配置
- [ ] `UIAP-E240`が演習ツリーに存在しない
- [ ] rv003usbの取得URLがコミット`75d926abe89a3002020b989015eab97ce5ad0470`を含む
- [ ] rv003usb取得時の実測SHA-256を`SOURCE_FILES.sha256`へ記録
- [ ] 3演習で`make -n build`が成功
- [ ] `01_macro_keyboard`でビルド、書き込み、`1209:C003`列挙、`AbCdE`入力を実機確認
- [ ] `02_rotary_cursor_size`でビルド、書き込み、`1209:C004`列挙、CW／CCW、サイズ変更、`Ctrl+C`復元を実機確認
- [ ] PoC用VID:PIDとシリアル番号を正式識別子として扱っていない
- [ ] rv003usbファイル単位SHA-256を最終リリース用期待値として固定

最後の4つの実機・正式固定項目が未完了の間、test17を参加者向け最終版として扱わない。

## 2026-08-01 Windows test18書き込みコマンド回帰検査

必須演習3本について、セットアップ後に次を確認する。

- [ ] Makefileの`FLASH_COMMAND`が、自動変数`$<`を含む場合は遅延評価`=`である
- [ ] `make -n flash`が終了コード0になる
- [ ] `00_onboard_led_blink`は`-w onboard_led_blink.bin flash -b`を含む
- [ ] `01_macro_keyboard`は`-w macro_keyboard.bin flash -b`を含む
- [ ] `02_rotary_cursor_size`は`-w rotary_cursor_size.bin flash -b`を含む
- [ ] `-w`の直後が`-b`または空になっていない
- [ ] `doctor`のNewlib判定は`make -n build`の実効コマンドを使用する
- [ ] 参加者向けMarkdownにNUL、SOH、STXなどの制御文字がない
- [ ] Windowsパスのバックスラッシュが改行または制御文字へ変換されていない

`0.6.0-test17`は、マクロキーボードのビルドには成功したが書き込みファイル名が空になったため、リリース候補として使用しない。`0.6.1-test18`は静的回帰検査済みであり、Windows実機の書き込みとHID動作を確認するまで参加者向け最終版として扱わない。詳細結果は`70_VALIDATION_RESULTS.md`を参照する。

## 2026-08-01 Windowsポインターサイズ反映の回帰検査

`02_rotary_cursor_size`のリリース候補では、HID受信とWindows設定変更を分離して確認する。

- [ ] `make app-dry-run`でCW／CCWを受信できる
- [ ] ホスト実装に`SPI_SETCURSORS`定数または同アクションの呼出しがない
- [ ] Windows即時反映方式が、現行検証基準の`SystemParametersInfoW`アクション`0x2029`を使用する
- [ ] `CursorBaseSize`と`Software\Microsoft\Accessibility\CursorSize`の両方を保存・復元する
- [ ] 前版形式の復元状態ファイルを移行できる
- [ ] `make cursor-test`でサイズ変更と復元が成功する
- [ ] `make app`でCW／CCWに応じてサイズが変化する
- [ ] `Ctrl+C`終了時に起動前サイズへ復元する
- [ ] USB切断または異常終了後に`make restore`で復元できる

`0x2029`は未文書化動作であるため、静的検査だけで合格にせず、Windows更新後を含む各リリース候補で実機確認する。具体的な不具合と復旧は`60_TROUBLESHOOTING.md`、検証事実は`70_VALIDATION_RESULTS.md`を正本とする。

<!-- Source: 60_TROUBLESHOOTING.md -->

# トラブルシューティング指針

更新日: 2026-08-01

この文書は、UIAPduino Pro Micro CH32V003 V1.4を使用するXP祭り2026向け開発環境、ファームウェア、USB HID、回路、PC側アプリケーションの問題を切り分けるための指針である。

過去のPoCで使用した一時的なVID:PID、USBシリアル番号、Devkitバージョンは、正式仕様として扱わない。

---

## 1. 基本方針

問題を次の層に分けて切り分ける。

1. ZIPの展開と開発環境の起動
2. PATH、環境変数、同梱ツール
3. 依存関係とビルド
4. ブートローダー検出と書き込み
5. アプリケーションUSB列挙
6. HIDレポート送受信
7. GPIO、回路、配線
8. PC側アプリケーション
9. OS設定の変更と復旧

複数の変更を同時に試さず、一段階ずつ確認する。

次の状態は別の成功段階として記録する。

- 開発環境起動成功
- セットアップ成功
- ビルド成功
- 書き込み成功
- アプリケーションUSB列挙成功
- HID送受信成功
- PC側処理成功
- 物理動作成功
- 再起動後の再現成功
- オンライン`setup`と固定取得物検証の成功

一段階の成功を、後続段階の成功として扱わない。

---

## 2. 最初に収集する情報

最低限、次を取得する。

- OS
- OSバージョン
- CPUアーキテクチャ
- UIAP Devkitバージョン
- 展開先
- 実行したコマンド
- 実行ディレクトリ
- 最初に表示されたエラー
- 完全なコンソール出力
- UIAPduinoの接続台数
- 使用USBケーブル
- USBハブの有無
- 外付け回路の有無
- 配線写真
- 直前に変更した内容
- 対象ファームウェアのVID:PID
- ブートローダーモードか通常動作モードか
- PC側アプリケーションを起動しているか
- 生成されたログファイル

利用できるDevkitでは、次を実行する。

```text
doctor
versions
report
```

従来構成では、次のスクリプトを使用する場合がある。

```sh
"$UIAP_DEVKIT_ROOT/scripts/doctor.sh"
"$UIAP_DEVKIT_ROOT/scripts/show-versions.sh"
```

コンソール出力は途中を省略せず、最初のエラーより前のコマンド行も含めて保存する。

---

## 3. 当日の最短復旧フロー

参加者の演習継続を優先する場合は、次の順に試す。

1. PC側アプリケーションを`Ctrl+C`で終了する
2. USBハブを外し、PCへ直結する
3. 外付け回路を外す
4. データ通信確認済みUSBケーブルへ交換する
5. UIAPduinoを1台だけ接続する
6. `start-uiap.cmd`または`start-uiap.command`から環境を開き直す
7. `doctor`を実行する
8. 既知の正常なLチカ演習で`make clean`、`make flash`を試す
9. 予備UIAPduinoへ交換する
10. 問題のボードは講師が回収し、SWIO復旧は終了後に行う

原因調査に時間がかかる場合は、予備ボード、配線済み見本、完成済みデモへ切り替える。

---

## 4. 開発環境が起動しない

確認項目:

- ZIPを完全に展開したか
- ZIP内から直接実行していないか
- 起動ファイルが最上位ディレクトリにあるか
- `runtime`、`scripts`、`workspace`が存在するか
- 展開先が極端に長くないか
- 展開先に空白や特殊文字が含まれていないか
- セキュリティソフトが実行ファイルを隔離していないか
- macOSで実行権限が保持されているか

Windowsでは次を使用する。

```text
start-uiap.cmd
```

macOSでは次を使用する。

```text
start-uiap.command
```

別のCommand Prompt、PowerShell、Windows Terminal、VS Codeターミナルから直接`make`を実行しない。

---

## 5. `UIAP_WORKSPACE is not set`

主な原因:

- 専用起動ファイルを使っていない
- 起動後に別のターミナルを開いた
- 起動スクリプトが途中で失敗した
- 環境を起動中にDevkitディレクトリを移動した

対応:

1. 現在のコンソールを閉じる
2. Devkitを移動した場合は、関連するすべてのコンソールを閉じる
3. 専用起動ファイルから開き直す
4. 次を確認する

Windows Command Prompt:

```text
echo %UIAP_DEVKIT_ROOT%
echo %UIAP_WORKSPACE%
```

POSIXシェル:

```sh
echo "$UIAP_DEVKIT_ROOT"
echo "$UIAP_WORKSPACE"
```

5. `doctor`を再実行する

固定パスを手動設定して回避しない。

---

## 6. `make`、コンパイラ、Pythonなどが見つからない

例:

```text
make: command not found
riscv-none-elf-gcc: command not found
python: command not found
```

確認:

- `setup`が完了しているか
- `runtime`以下のツールが存在するか
- 専用起動ファイルから起動したか
- PATHがDevkit内ランタイムを指しているか
- セキュリティソフトに削除されていないか
- macOSバイナリがarm64か
- Windows x64用バイナリをWindows ARM64で直接使用していないか

Windowsネイティブ検証版では、次を実行する。

```text
setup
doctor
versions
```

セットアップ途中で失敗した場合は、エラーを修正してから`setup`を再実行する。正常なダウンロード済みファイルは再利用できる構成を優先する。

---

## 7. `ch32fun`または`rv003usb`が見つからない

確認する場所:

```text
workspace/deps/ch32fun
workspace/deps/rv003usb
```

旧例:

```make
CH32FUN = ../ch32fun
RV003USB = ../rv003usb
```

推奨:

```make
CH32FUN_ROOT ?= $(UIAP_WORKSPACE)/deps/ch32fun
CH32FUN ?= $(CH32FUN_ROOT)/ch32fun
RV003USB ?= $(UIAP_WORKSPACE)/deps/rv003usb
```

確認項目:

- `setup`が依存関係の展開まで完了したか
- `workspace/deps/VERSIONS.md`に固定コミットが記録されているか
- Makefileが旧配置を参照していないか
- `.git`を削除した配布版でもコミットIDが残っているか
- `workspace/deps/ch32fun/SUBSET.md`、`UPSTREAM_COMMIT`、`ALLOWLIST.txt`が存在するか
- `ch32fun/ch32fun.mk`、必要ヘッダー、リンカースクリプトが許可リストから欠落していないか
- 完全版上流ツリーを手動コピーしてサブセットを上書きしていないか

ワークショップ中に最新版または完全版上流ツリーを取得して置き換えない。正常な配布ZIPから`workspace/deps/ch32fun`を復元する。

---

## 8. 一般的なビルドエラー

次の順に切り分ける。

```text
make clean
make
```

確認項目:

1. 最初のエラー
2. 実行ディレクトリ
3. `TARGET`と主ソース名
4. `CH32FUN`と`RV003USB`
5. コンパイラバージョン
6. 対象MCUとパッケージ
7. 文字コードと改行
8. ファイル名の大文字小文字
9. Windows予約名
10. 直前の編集差分

後続の大量エラーより、最初のエラーを優先する。

`rv003usb.S`から次が表示される場合がある。

```text
#warning "CH32V003"
```

対象MCUを示す既知のプリプロセッサ警告であり、リンクとバイナリ生成が成功していれば、単独では失敗原因ではない。

---

## 9. `No rule to make target '<TARGET>.c'`

例:

```text
make: *** No rule to make target 'vibration_motor_poc.c', needed by 'vibration_motor_poc.elf'. Stop.
```

主な原因:

- `TARGET`に対応する主ソースが存在しない
- ファイル名変更後にMakefileを更新していない
- 大文字と小文字が一致しない
- 別ディレクトリで`make`を実行した

確認:

POSIXシェル:

```sh
pwd
ls -la
grep '^TARGET' Makefile
```

Windows Command Promptでは、現在位置とファイル一覧を確認する。

```text
cd
dir
findstr /B "TARGET" Makefile
```

対応:

- 主ソースを`$(TARGET).c`へ合わせる
- Makefileへソース一覧を明示する
- 正しい演習ディレクトリへ移動する
- 修正後に`make clean`、`make`を実行する

---

## 10. Windowsパスが崩れ、`generated__.ld`を作成できない

代表例:

```text
sh: can't create C:pjxpfes2026uiap-devkit-win64workspace/deps/ch32fun/ch32fun/generated__.ld: nonexistent directory
```

または:

```text
can't create C:...generated__.ld
```

主な原因:

- Windows形式のパス`C:\...`をPOSIX互換`sh`へそのまま渡した
- バックスラッシュがエスケープとして処理され、区切り文字が消えた

問題のある形式:

```text
C:\pj\xpfes2026\uiap-devkit-win64
```

シェルへ渡す形式:

```text
C:/pj/xpfes2026/uiap-devkit-win64
```

恒久対応:

Makefile内部で、外部コマンドへ渡すパスだけを正規化する。

```make
UIAP_WORKSPACE_POSIX := $(subst \,/,$(UIAP_WORKSPACE))
CH32FUN := $(UIAP_WORKSPACE_POSIX)/deps/ch32fun
RV003USB := $(UIAP_WORKSPACE_POSIX)/deps/rv003usb
```

環境変数自体はWindows形式のまま保持してよい。

確認:

- GCCコマンド行の依存パスが`C:/...`になっている
- `generated__.ld`の出力先が`C:/...`になっている
- `doctor`のパス互換性検査が成功する

修正版確認後:

```text
make clean
make
make flash
```

この問題はDevkit `0.1.0-test2`で修正確認済みである。

---

## 11. 旧MSYS2手順または別Devkit版を使用している

現行Windows版は、MSYS2を使用しないxPackベースのWindowsネイティブ構成である。

確認項目:

- 使用中Devkitの`VERSION`
- `start-uiap.cmd`の表示
- `runtime/build-tools`、`runtime/toolchain`、`runtime/python`が存在するか
- `runtime/msys64`が残っていないか
- 手順書が同じDevkit版を対象としているか
- 任意のMSYS2、Git Bash、WSL、別のCommand Promptから`make`していないか

対応:

1. 現在のコンソールを閉じる
2. Devkitトップレベルの`start-uiap.cmd`から開き直す
3. `doctor`と`versions`を実行する
4. 現行版の手順書だけを使用する

過去のMSYS2構成で確認したPoC結果は履歴として有効だが、その起動方法や復旧手順を現行Devkitへ適用しない。

---

## 12. `setup`中のhidapi確認で`SyntaxError`

代表例:

```text
File "<string>", line 1
    import hid; print(hidapi
                     ^
SyntaxError: '(' was never closed
[UIAP-E207] Bundled Python could not import hidapi.
```

主な原因:

- PowerShell、cmd.exe、Pythonの複数段階で引用符が解釈された
- `python -c`へ渡したコードが途中で切れた
- hidapiのインストール失敗ではなく、検証コマンド自体の構文エラー

確認:

- `runtime/python/Lib/site-packages`にhidapiの`.pyd`が存在する
- エラーが`import hid`ではなく`SyntaxError`である
- Devkitバージョンが`0.3.0-test5`以前ではないか

恒久対応:

複雑なPythonコードを`python -c`で実行しない。診断コードを`.py`ファイルへ分離する。

例:

```text
scripts/python/hidapi_probe.py
```

PowerShellからは、Pythonファイルを引数として実行する。

修正後:

```text
setup
doctor
```

正常時の例:

```text
Python: 3.14.6
hidapi: ...\hid.cp314-win_amd64.pyd
hidapi import: PASS
```

この問題はDevkit `0.3.1-test6`で修正確認済みである。

---

## 13. macOS固有

### 実行権限

確認:

```sh
ls -l start-uiap.command
ls -l scripts
ls -l runtime/bin
```

ZIP展開後も、起動ファイル、スクリプト、実行ファイルに実行権限があることを確認する。

### Gatekeeper

- 表示された警告内容と対象ファイルを記録する
- 一度起動を試みた後、macOS標準のPrivacy & Securityから対象を確認する
- 無差別な隔離属性削除を標準手順にしない
- `sudo spctl --master-disable`を案内しない

### アーキテクチャ違い

```sh
file runtime/bin/minichlink
otool -L runtime/bin/minichlink
```

Intel用バイナリやHomebrew固有パスが残っていないか確認する。

macOS Apple Siliconでの実機ビルド、書き込み、HID、ホストアプリは、Windowsの成功だけを根拠に確認済みとしない。

---

### 13.1 「Appleは、start-uiap.commandに悪質なソフトウェアが含まれていないことを検証できません」

主な原因:

- 検証版ZIPがApple Developer IDで署名・公証されていない
- ブラウザから取得したファイルに隔離属性が付いている

対応:

1. 警告画面を閉じる
2. 「システム設定」→「プライバシーとセキュリティ」を開く
3. `start-uiap.command`の「このまま開く」を選ぶ
4. 対象ファイル名と入手元を確認して個別に許可する

Gatekeeper全体を無効化しない。`sudo spctl --master-disable`やDevkit全体への無差別な隔離属性削除を案内しない。

### 13.2 `cd: .../Downloads/workspace: No such file or directory`

Devkit `0.1.1-test2`で確認した回帰不具合である。

原因:

- `scripts/env.sh`が、自身のファイル位置ではなく呼び出し元の`$0`を基準にDevkitルートを解決した
- Devkitルートを`.../Downloads`と誤認し、`.../Downloads/workspace`へ移動した

恒久対応:

- `start-uiap.command`自身の配置ディレクトリをDevkitルートとして明示する
- 読み込まれるシェルスクリプト内で、呼び出し元の`$0`だけに依存しない
- 展開先を変更した回帰テストを行う

この問題は`0.1.2-test3`で修正確認済みである。

### 13.3 `[FAIL] make wrapper could not start /usr/bin/make.`

Devkit `0.1.2-test3`で確認した不具合である。

原因:

- macOS標準の`/usr/bin/make`を使用できると仮定していた
- Xcode Command Line Toolsがない環境では利用できなかった
- HomebrewやXcode Command Line Toolsを必須にしない方針に反する

恒久対応:

- GNU Make 4.4.1 arm64をDevkit内部へ配置する
- 参加者向け`make`ラッパーからDevkit内`gmake`だけを起動する
- Devkit内Makeがない場合はシステムMakeへフォールバックせず、`UIAP-E202`で停止する

この問題は`0.1.3-test4`で修正確認済みである。

### 13.4 `doctor`が`UIAP-E299`で終了する

`0.1.7-test8`では、次が意図的に残っている。

```text
[WARN] ch32fun is a test subset, not the final reviewed allowlist subset.
[FAIL] Bundled Python is not installed.
PASS=32 WARN=1 FAIL=1
```

これは`minichlink`やLチカ書き込みの失敗ではない。`test8`では、`setup`、`build-minichlink`、`make flash`、基板上LED点滅まで確認済みである。

参加者向けリリースとしては、Python・hidapiと最終`ch32fun`許可リストが未完了であるため不合格とする。`UIAP-E299`を無視して参加者向け最終版として配布しない。

### 13.5 Lチカビルドは成功するが`-I/usr/include/newlib`が表示される

`0.1.3-test4`の実機ビルドでは、このオプションが表示されたままFLASH 444 B、RAM 0 Bでビルドに成功した。

ただし、最終版でOS標準パスへ依存してよいことを意味しない。次を確認する。

- 当該パスを削除してもxPackツールチェーン内のファイルだけでビルドできるか
- `/usr/include/newlib`が存在しない別のMacでも成功するか
- 全演習で同じ結果になるか

不要ならMakefileまたは上流ビルド設定から削除する。


### 13.6 `make flash`が`Killed: 9`で終了する

代表例:

```text
.../runtime/bin/minichlink ...
gmake: *** [...: cv_flash] Killed: 9
```

`0.1.6-test7`の実機では、ローカル生成した`minichlink`へブラウザ由来の`com.apple.quarantine`が継承され、Gatekeeperが実行を拒否していた。

確認:

```sh
MINICHLINK="$UIAP_RUNTIME/bin/minichlink"
file "$MINICHLINK"
codesign --verify --verbose=4 "$MINICHLINK"
xattr -l "$MINICHLINK" 2>&1 || true
```

`com.apple.quarantine`が表示された場合、主催者が当該Macで生成した`minichlink`単体に限り、`build-minichlink`を再実行する。`0.1.7-test8`以降は、単体の隔離属性除去、アドホック署名、署名検証を自動化する。

手動診断が必要な主催者検証時だけ、対象と来歴を確認した上で次を使う。

```sh
xattr -d com.apple.quarantine "$MINICHLINK"
codesign --force --sign - "$MINICHLINK"
codesign --verify --verbose=4 "$MINICHLINK"
```

禁止事項:

- Devkit全体への`xattr -dr`
- Gatekeeper全体の無効化
- 入手元不明バイナリへの同手順適用
- 署名後の`strip`またはバイナリ編集

### 13.7 `Error: Could not initialize b003boot programmer`

代表例:

```text
VID:0x1209, PID:0xb803
Error: Could not initialize b003boot programmer
```

この表示では`minichlink`自体は起動している。主な確認対象はUSBブートローダー待機状態である。

確認順序:

1. UIAPduinoを1台だけ接続する
2. データ通信対応USBケーブルを使う
3. USBハブを外してMacへ直結する
4. RESETを押したままUSBを接続する
5. 約1秒後にRESETを離す
6. 直ちに`make flash`を実行する

成功表示:

```text
Halting Boot Countdown
Detected CH32V003
Writing image
Image written.
Booting
```

`0.1.7-test8`の実機では、最初の試行で初期化に失敗した後、ブートローダーモードへ入り直して直ちに再実行すると成功した。単一結果だけを根拠に原因を断定せず、ケーブル、ポート、接続台数、RESET操作、待機時間を順に切り分ける。

## 14. 一般的な書き込み失敗

確認:

- UIAPduinoを1台だけ接続しているか
- USBケーブルがデータ通信対応か
- ブートローダーモードに入っているか
- USBハブを外してPCへ直結したか
- 外付け回路を一旦外したか
- 別のUSBポートを試したか
- 別のUIAPduinoで再現するか
- ブートローダーVID:PIDが正しいか
- `minichlink`の最初のエラーが何か

手動フォールバック:

1. USBケーブルを抜く
2. RESETを押したままUSBを接続する
3. RESETを離す
4. `make flash`を実行する

書き込み成功の代表表示:

```text
VID:0x1209, PID:0xb803
Halting Boot Countdown
Detected CH32V003
Image written.
Booting
```

---

## 15. `VID:0x1209, PID:0xb003`の後に初期化できない

例:

```text
VID:0x1209, PID:0xb003
Error: Could not initialize any supported programmers
```

この表示は、UIAPduinoを検出したことではなく、`minichlink`が`1209:B003`を探していることを示す場合がある。

Windows書き込みPoCで確認済みのブートローダーVID:PID:

```text
1209:B803
```

Makefileまたは共通書き込み設定を確認する。

```text
-c 0x1209b803
```

`make`の最終表示が`Error 127`でも、直前に`minichlink`のバージョンが表示されている場合は、単純な「コマンドが見つからない」とは限らない。最初に表示された`minichlink`のエラーを確認する。

---

## 16. `[UIAP-F205] Multiple bootloaders were detected`

代表例:

```text
[UIAP-F205] Multiple bootloaders were detected.
Disconnect boards until only one remains.
```

考えられる原因:

1. 実際に複数のUIAPduinoがブートローダーモード
2. 1台の物理USBデバイスについて、親USBデバイスとHID子デバイスを別々に数えた
3. 切断済みPnPエントリを現在接続中として数えた

確認:

- 接続しているUIAPduinoの台数
- `USB\VID_1209&PID_B803\...`形式の現在接続中の親デバイス数
- `HID\VID_1209&PID_B803\...`を物理ボード数へ含めていないか
- `Status`が`OK`または現在接続中を示しているか

恒久対応:

- 物理USB親デバイスだけを数える
- 子HIDインターフェースを除外する
- 現在接続中のデバイスだけを対象にする
- 2台以上の場合は、対象インスタンスIDを表示して書き込みを中止する

正常時:

```text
[UIAP] One physical bootloader detected. Starting flash.
[UIAP] Bootloader: USB\VID_1209&PID_B803\...
```

この問題はDevkit `0.2.1-test4`で修正確認済みである。

---

## 17. `1209:B803`を検出できない

確認:

- RESETを押したままUSBを接続し、離したか
- Windowsのデバイス一覧に`VID_1209&PID_B803`が存在するか
- アプリケーションモードのVID:PIDだけが見えていないか
- USBケーブルがデータ通信対応か
- USBハブを外したか
- 外付け回路を外したか
- 別のUSBポートまたはPCで認識するか

アプリケーション用のPoC VID:PIDをブートローダーと混同しない。

PoCで使用した例:

```text
1209:C003
1209:C004
1209:D003
```

これらはアプリケーション側の一時値であり、ブートローダー`1209:B803`とは異なる。

ブートローダー自体が破損している場合は、当日は予備ボードへ交換し、SWIO復旧は講師の事後作業とする。

---

## 18. 書き込み成功後にアプリケーションを検出できない

代表的な状態:

```text
Image written.
Booting
```

までは成功するが、その後に期待VID:PIDが見つからない。

確認:

- ファームウェア側VID:PID
- 書き込みスクリプトの期待VID:PID
- USB Product文字列
- USBシリアル番号
- Report Descriptor
- `rv003usb`初期化
- USB用GPIOと外付け回路の競合
- 書き込み後の待機時間
- WindowsのPnP更新遅延

対応:

1. 20秒程度待つ
2. USBを抜いて通常接続し直す
3. 対象演習へ`cd`で移動する
4. `make hidcheck`または演習のデバイス列挙ターゲットを実行する
4. Windows Device ManagerまたはPnP一覧で確認する
5. 既知の正常なLチカまたはHIDサンプルへ戻す

書き込み成功とアプリケーションUSB列挙成功を別の判定として記録する。

---

## 19. USBデバイスとして認識されない

切り分け:

1. ケーブル交換
2. USBポート変更
3. USBハブを外す
4. 外部回路を外す
5. 既知の正常ファームウェアを書き込む
6. OSのUSB一覧を確認する
7. VID:PIDを確認する
8. Descriptorを確認する
9. 別PCで確認する

電源LEDが点灯していても、データ線が利用できるとは限らない。

Windowsでは、1台のUSB HIDデバイスが次のように複数行で表示される場合がある。

```text
USB 入力デバイス
HID キーボード デバイス
```

これは親USBデバイスとHIDインターフェースであり、必ずしも物理ボードが複数あることを意味しない。

---

## 20. HID入力が反応しない

確認:

- Report Descriptor
- Reportサイズ
- Report ID
- Usage PageとUsage
- Endpoint
- ポーリング間隔
- Input Reportの送信条件
- デバウンス
- GPIOのアクティブHigh/Low
- OS側で別用途として解釈されていないか
- ホスト側が正しいインターフェースを開いているか

既知の最小HIDサンプルへ戻して比較する。

ファームウェアがレポートを送っているか不明な場合は、ホスト側アプリケーションに`--dry-run`や生レポート表示を用意する。

---

## 21. HIDマクロキーボードが文字を入力しない

検証済み配線:

```text
D5 / PC3 ─ モメンタリスイッチ ─ GND
```

内部プルアップを使用し、押下時Lowとする。WindowsとmacOSの実機で、押下1回による`AbCdE`入力を確認済みである。

### 21.1 共通確認

- テキストエディットやメモ帳など安全な入力先へフォーカスがあるか
- 日本語IMEがOFF、英数またはABC入力か
- Caps LockがOFFか
- スイッチがD5とGNDの間に接続されているか
- 押し続けではなく、一度離してから再度押しているか
- キー押下レポートの後に全キー解放レポートを送っているか
- 大文字にShift修飾を付けているか

### 21.2 macOSでUSBには見えるがHIDとして見えない

USB Device列挙を確認する。

```sh
ioreg -p IOUSB -l -w 0 > /tmp/uiap-usb.txt
grep -n -B 12 -A 24 -E \
'UIAP Macro Keyboard|"idVendor" = 4617|"idProduct" = 49155' \
/tmp/uiap-usb.txt
```

HID列挙を確認する。

```sh
hidutil list > /tmp/uiap-hid.txt
grep -i -E 'UIAP|0x1209|0xc003|4617|49155' /tmp/uiap-hid.txt
```

判定:

| `ioreg` | `hidutil` | 判定 |
|---|---|---|
| 表示なし | 表示なし | USB列挙前または途中で失敗 |
| 表示あり | 表示なし | USB Device列挙は成功、IOHIDバインドは失敗 |
| 表示あり | 表示あり | HID入力レポートまたは入力先を調査 |

`0.1.8-test9`では、`ioreg`に`1209:C003`が現れ、`bDeviceClass = 3`だったが、`hidutil list`には現れなかった。同じデバイスはWindowsで`AbCdE`を入力できた。この症状では、配線やキーシーケンスより先にDescriptorとHIDクラス要求を確認する。

修正要件:

- Device Descriptorのクラス3フィールドを`0`
- HIDクラスはInterface Descriptorで宣言
- `GET_REPORT`
- `GET_IDLE`、`SET_IDLE`
- `GET_PROTOCOL`、`SET_PROTOCOL`

### 21.3 macOSのキーボード設定アシスタント

初回接続時に「左Shiftキーの右隣のキーを押してください」と表示される場合がある。マクロデバイスには該当キーが存在しない。

対応:

1. Mac本体のキーを代わりに押さない
2. 前の画面へ戻る
3. 1ページ目の「終了」を押して閉じる
4. 安全なテキスト入力欄でスイッチを押す

macOS 26.5.2の確認環境では「スキップ」ボタンは表示されなかった。「終了」で閉じた後に`AbCdE`を入力でき、USB再接続後も入力できた。再接続時にはアシスタントは再表示されなかった。

### 21.4 安全上の注意

次へフォーカスを置いた状態で試さない。

- コマンドプロンプト
- PowerShell
- Terminal
- ブラウザのアドレス欄
- パスワード入力欄
- 管理画面

意図しない入力が続く場合は、直ちにUSBケーブルを外す。

---

## 22. HID Output ReportまたはFeature Reportが届かない

確認:

- Report Descriptorの定義
- Report ID
- ホストAPIが要求するレポート長
- 先頭にReport IDが必要か
- Control TransferかInterrupt OUTか
- ファームウェアとホスト側でVID:PIDが一致しているか
- WindowsとmacOSでのAPI差
- デバイス側の受信処理
- 送信したバイト列とデバイス側仕様の対応

Feature Reportでは、ホストAPIによって送信バッファ先頭にReport IDが必要になる。

複数のレポート形式がある場合は、Report IDごとの長さを表で管理する。

---

## 22.1 `sample`、`macro`、`cursorapp`などが見つからない

現行方針では正常である。これらは演習移動または特定演習操作を隠す旧トップレベル別名であり、参加者向け標準コマンドとして配布しない。

対応例:

ロータリーエンコーダー演習:

```text
cd /d "%UIAP_WORKSPACE%\exercises\02_rotary_cursor_size"
make help
make hidcheck
make app
```

HIDデバイス一覧:

```text
make list
```

異常終了後のポインター設定復元:

```text
make restore
```

`cursorstore`という標準コマンドは存在しない。復元は`make restore`を使用する。

旧コマンドを復活させたり、参加者のPATHへ個別ラッパーを追加したりしない。実行場所が不明な場合は、Windowsでは`cd`、macOSでは`pwd`で現在位置を確認する。

---

## 23. ホスト側プログラムがHIDデバイスを見つけない

### 最初に配置を確認する

演習固有のPC側Pythonプログラムの標準配置は次である。

```text
workspace/exercises/<exercise-name>/host/<program>.py
```

ロータリーエンコーダー演習:

```text
workspace/exercises/02_rotary_cursor_size/host/cursor_size_host.py
```

次の旧パスを実行時の標準として使用しない。

```text
workspace/host/cursor_size_host.py
```

`make app`でファイルが見つからない場合は、Makefile、コマンドラッパー、READMEが旧パスを参照していないか確認する。別演習の`host`へコピーして回避せず、対応する演習の`host`へ配置して参照を修正する。

`scripts/python`はDevkit全体の診断・復旧用であり、演習固有ホストアプリの移動先ではない。

確認:

- 書き込み後に通常アプリケーションとして再列挙されたか
- ホスト側VID:PIDがファームウェアと一致するか
- Usage PageとUsageが一致するか
- 製品名が一致するか
- USBシリアル番号が一致するか
- 同一VID:PIDの別デバイスが接続されていないか
- hidapiが列挙するインターフェースが複数ないか
- ホストアプリが古い設定値を保持していないか

PoCの一時値:

```text
1209:C003  HIDマクロキーボード
1209:C004  ロータリーエンコーダー入力
1209:D003  振動モーター制御
TEST3-001  一時USBシリアル番号
TEST7-001  一時USBシリアル番号
```

これらを正式配布用識別子として扱わない。

書き込み直後に見つからない場合:

1. PC側アプリケーションを終了する
2. USBを抜く
3. 通常接続し直す
4. `cd /d "%UIAP_WORKSPACE%\exercises\02_rotary_cursor_size"`で演習へ移動する
5. `make hidcheck`または`make list`を実行する
5. PC側アプリケーションを再起動する

---

## 24. hidapiをimportできない

確認:

- 同梱Pythonのバージョン
- wheelのPython ABI
- Windows x64用wheelか
- `.pyd`が`site-packages`に存在するか
- Visual C Runtimeなど追加依存が必要でないか
- システムPythonではなく同梱Pythonを使用しているか

診断:

```text
doctor
versions
```

正常時の例:

```text
hidapi import: PASS
```

`SyntaxError`の場合は、hidapi本体より先に「12. `setup`中のhidapi確認で`SyntaxError`」を確認する。

---

## 25. ロータリーエンコーダーが反応しない

2026-07-24に確認した3端子型RE12000XH1-V02の配線:

| UIAPduino | エンコーダー | 用途 |
|---|---|---|
| D8 / PC6 | A | A相、内部プルアップ |
| GND | C | 共通端子 |
| D9 / PC7 | B | B相、内部プルアップ |

注意:

- `3.3V`または`5V`へ接続しない
- 左右の固定タブへ接続しない
- D5はモメンタリスイッチ用として使用し、エンコーダーには使わない
- 配線変更前にUSBを外す

確認:

- A、C、Bの向きを取り違えていないか
- 軸側と端子側で左右が反転して見えていないか
- CがGNDへ接続されているか
- D8とD9が内部プルアップ入力か
- Vendor-defined HIDデバイスが列挙されているか
- 演習ディレクトリの`make app-dry-run`で回転イベントが表示されるか
- 1クリック分をゆっくり回して反応するか

D5に既存スイッチが接続されていても、エンコーダーファームウェアがD5を初期化・参照しなければ競合しない。

---

## 26. エンコーダーの方向が逆、1クリックで複数回動く、取りこぼす

### 回転方向が逆

対応候補:

1. PC側アプリケーションを逆方向モードで起動する

```text
make app-reverse
```

2. D8とD9を入れ替える
3. ファームウェアの方向反転設定を変更する

### 1クリックで2段階以上動く

主な原因:

- 1クリックあたりの有効エッジ数設定が製品と一致しない
- 接点バウンス
- 不正遷移を破棄していない
- A/B相のサンプリングが速すぎる、または遅すぎる

確認:

- `UIAP_COUNTS_PER_DETENT`
- 4エッジを1クリックとして扱っているか
- 不正な2ビット遷移を破棄しているか
- ログのSequence番号とDelta
- `--dry-run`でOS設定を変えずにイベントだけ確認できるか

検証済み製品では、24クリック／24パルスとして、4つの有効A/Bエッジを1クリックへ集約する構成を使用した。

### 高速回転で取りこぼす

- メインループの他処理を減らす
- USB処理を長時間停止しない
- サンプリング周期を確認する
- イベントを1回ずつではなく累積Deltaとして送る案を検討する

---

## 27. PC側アプリケーションを起動してもポインターサイズが変わらない

確認:

- `make app`のコンソールにCW/CCWログが出るか
- 演習ディレクトリの`make app-dry-run`ではイベントが見えるか
- Windowsポインターサイズが既に上限または下限でないか
- ホストアプリが正しいHIDデバイスを開いているか
- Windows設定変更APIが成功しているか
- レジストリフォールバックが実行されたか
- HIDと分離した`make cursor-test`が成功するか
- `CursorBaseSize`と`Accessibility\CursorSize`の保存値が一致するか
- v1.0.7以降のWindows即時反映処理を使用しているか
- 別のアクセシビリティ設定が上書きしていないか

切り分け:

1. HIDイベントが来ない  
   → ファームウェア、配線、HID列挙を確認
2. HIDイベントは来るがサイズが変わらない  
   → Windows設定変更処理を確認
3. ログ上はサイズが変わるが見た目が変わらない  
   → カーソル再読み込み、テーマ、OS設定を確認

管理者権限を要求する回避策を標準手順にしない。

`make cursor-test`で`[WinError 6] ハンドルが無効です`となる場合、v1.0.6の追加`SPI_SETCURSORS`呼出しを使用している可能性がある。v1.0.7以降へ更新し、先に`make restore`、次に`make cursor-test`を実行する。Windowsサイズ即時反映で使用する`0x2029`は未文書化動作であり、このプロジェクトではWindows 11 x64実機確認済みPoCとして限定する。

---

## 28. PC側アプリ終了後にポインターサイズが元へ戻らない

正常終了では、`Ctrl+C`を使用する。

```text
Ctrl+C
```

正常なアプリは、起動時サイズを保存し、終了時に復元する。

強制終了、PCクラッシュ、ターミナル強制終了などで復元されなかった場合:

```text
make restore
```


確認:

- 起動時サイズがログに記録されているか
- 復元処理の成否が表示されるか
- Windows設定画面から手動で戻せるか

OS設定を変更するホストアプリには、必ず次を用意する。

- 起動時値の記録
- `Ctrl+C`終了処理
- 明示的な復元コマンド
- 異常終了時の手動復旧手順

---

## 29. USB切断時にPC側アプリが停止する、または再接続しない

現在のワークショップ方針では、自動再接続は必須としない。

期待する動作:

- 切断を検出する
- 明確なエラーを表示する
- ログを保存する
- OS設定を可能な範囲で復元する
- 非ゼロ終了コードで終了する

復旧:

1. PC側アプリケーションを終了する
2. UIAPduinoを通常接続する
3. `cd /d "%UIAP_WORKSPACE%\exercises\02_rotary_cursor_size"`で演習へ移動する
4. `make hidcheck`または`make list`で確認する
5. `make app`を再実行する

切断中に無限ループで待ち続ける実装を標準にしない。

---

## 30. ドライバー内蔵振動モーターモジュールが動かない

確認:

- モジュールの`VCC`が指定電源へ接続されているか
- `GND`がUIAPduinoと共通か
- `IN`が正しいGPIOか
- `VCC`と`IN`を取り違えていないか
- High/LowまたはPWMが出ているか
- まず100%出力で始動するか
- モジュールの動作電圧と始動電圧を満たしているか

UIAPduino V1.4で確認済みの振動モーターPoC:

```text
D6/A2 → PC4 → TIM1_CH4
```

低いPWMレベルだけ始動しない場合は、キックスタート未実装または始動トルク不足を疑う。

モーターは動いているが弱くて気づけない場合は、`make haptic-test HAPTIC_LEVEL=1`から`5`まで比較する。`03_pot_cursor_haptic`の確認済み既定値はレベル4で、80ms ONを2回、間隔40msである。電源電圧を定格外へ上げず、ON時間と回数で知覚性を調整する。

---

## 31. 裸のモーターが動かない

確認:

- モーター電源
- GND共通
- MOSFETまたはトランジスタの向き
- ゲートまたはベース信号
- ゲートプルダウン
- フライバックダイオードの向き
- PWMデューティ
- 起動電流
- モーター単体動作

モーター本体をGPIOへ直接接続しない。

---

## 32. OFFにしてもモーターが停止しない

確認:

- `IN`端子の接続先
- GPIO割り当て
- PWMチャネルの無効化
- GPIOがLowへ戻っているか
- Report IDと受信値
- PC側がOFFコマンドを送信したか

停止しない場合は直ちにUSBを抜く。

参加者向けファームウェアでは、OFF時にPWMを無効化し、GPIO Lowへ戻す構成を優先する。

---

## 33. モーター動作でUSBが切れる

想定原因:

- 突入電流
- 電源電圧降下
- 逆起電力
- デカップリング不足
- GNDノイズ
- USB電源容量不足

対応候補:

1. USBハブを外してPCへ直結する
2. USBケーブルを交換する
3. 配線を短くする
4. モジュール近傍へ`0.1uF`を追加する
5. `47uF`～`220uF`程度のバルクコンデンサを検討する
6. PWM立ち上げまたはキックスタートを見直す
7. 必要ならモーター用電源分離を検討する
8. 外部電源を使う場合はGNDを共通化し、逆流を確認する

発熱、異臭、断続的リセットがある場合は直ちにUSBを外す。

---

## 34. `status`表示と実際の振動が一致しない

`status`がファームウェア保持値を返す実装では、表示は実際の回転数や振動量の測定値ではない。

確認:

- READMEに`status`の意味が明記されているか
- 低いPWMレベルでモーターが始動しているか
- 機械的負荷や固定方法が変わっていないか
- 電源電圧が低下していないか

必要なら、加速度センサーなど別の測定手段を使用する。

---

## 35. ログとサポートレポート

PC側アプリケーションは、原則として次へログを保存する。

```text
logs/
```

例:

```text
logs/cursor-YYYYMMDD-HHMMSS.log
```

ログに含める項目:

- Devkitバージョン
- アプリケーション名
- VID:PID
- 製品名
- USBシリアル番号
- Usage PageとUsage
- 接続、切断
- 受信イベント
- OS設定変更
- 復元結果
- 最初のエラー

ログに含めない項目:

- 不要なユーザー名
- ホームディレクトリ
- 個人情報
- 無関係なUSBデバイスのシリアル番号

ログが多すぎる場合は、規定されたローテーションと`make clean-logs`を使用する。

生成AIまたは講師へ渡す場合は、`report`の出力と、問題が発生した演習のログ末尾を添付する。

---

## 36. 主なエラーコード

| コード | 概要 | 主な確認先 |
|---|---|---|
| `UIAP-E207` | 同梱Pythonからhidapiをimportできない | hidapi、Python ABI、引用符 |
| `UIAP-E208` | hidapi診断スクリプト実行失敗 | Pythonファイル、ランタイム |
| `UIAP-E224` | minichlinkに隔離属性が残っている | `build-minichlink`、xattr、来歴 |
| `UIAP-E225` | minichlinkコード署名検証失敗 | 署名順序、バイナリ変更 |
| `UIAP-E311` | MakefileのWindowsパス互換性検査失敗 | `C:/...`正規化 |
| `UIAP-F205` | ブートローダーを複数検出 | 物理USB親デバイス数 |

エラーコードは、同じ原因に同じ番号を割り当てる。番号の意味をリリース間で変更しない。

---

## 37. 参加者対応

当日は、問題を完全に解決することより、演習を継続できることを優先する。

用意する復旧手段:

- 予備USBケーブル
- 予備UIAPduino
- 既知の正常な演習フォルダ
- 復旧用ファームウェア
- 講師PC
- 配線済み見本
- 完成済みデモ
- 別USBポート
- 外部回路を外した最小構成
- PC側設定の復元コマンド
- 検証済みの旧Devkit ZIP

参加者にZadig、USBドライバー変更、管理者権限が必要な操作を行わせない。

---

## 38. 新しい問題の記録

新しい問題が見つかった場合は、次を記録する。

- 症状
- 対象OS
- Devkitバージョン
- 対象演習
- 対象ボード
- 使用部品
- 配線
- 再現手順
- 実行コマンド
- 最初のエラー
- 原因
- 一時回避策
- 恒久対応
- 修正版リリース
- 検証済みの範囲
- 未検証の範囲
- 再発防止の自動検査

重要な決定変更は`90_DECISIONS.md`にも反映する。

---

## 39. PoC識別子の扱い

2026-07-24までのPoCでは、次の一時値を使用した。

```text
1209:C003
1209:C004
1209:D003
TEST3-001
TEST7-001
```

これらは、正式な公開配布用VID:PIDまたはUSBシリアル番号として決定されていない。

次を行うまで正式仕様として使用しない。

- VID:PIDの利用権確認
- アプリケーションPIDの決定
- MCU固有ID由来USBシリアル番号の検証
- 同一VID:PIDでの複数台接続試験
- WindowsとmacOS双方での列挙確認

## 39. ch32funサブセットのファイルが不足している

代表例:

```text
No such file or directory: .../ch32fun/ch32fun.mk
fatal error: ch32fun.h: No such file or directory
cannot find .../misc/libgcc.a
minichlink source or executable was not found
```

主な原因:

- 許可リストへ必要ファイルを追加していない
- 上流更新後にファイル配置が変わった
- サブセット生成が途中で失敗した
- セキュリティソフトがファイルを隔離した
- 参加者が`workspace/deps/ch32fun`を手動編集した
- 別の不完全なサブセットで上書きした

確認:

```text
workspace/deps/ch32fun/LICENSE
workspace/deps/ch32fun/SUBSET.md
workspace/deps/ch32fun/UPSTREAM_COMMIT
workspace/deps/ch32fun/ALLOWLIST.txt
workspace/deps/ch32fun/ch32fun/ch32fun.mk
workspace/deps/ch32fun/ch32fun/ch32fun.h
workspace/deps/ch32fun/ch32fun/ch32fun.ld
```

対応:

1. `doctor`または依存関係検査を実行する
2. `UPSTREAM_COMMIT`と`workspace/deps/VERSIONS.md`を確認する
3. 参加者PCでは正常な配布ZIPから`workspace/deps/ch32fun`を復元する
4. リリース作業では、完全版上流ツリーから許可リスト生成を再実行する
5. 欠落ファイルを手作業でコピーせず、許可リストへ追加する
6. WindowsとmacOSの全採用演習を再検証する

当日の演習では、原因調査に時間がかかる場合は正常な予備Devkitまたは講師PCへ切り替える。

## 40. ch32funサブセットへ許可外ファイルが混入している

症状:

- `examples_v30x`、`examples_usb`などが参加者向けZIPに存在する
- `platformio.ini`や`projects`が残っている
- `ALLOWLIST.txt`にないファイルが存在する
- 同じバージョンのZIPでファイル一覧が異なる

主な原因:

- 完全版上流ツリーを直接上書きした
- 削除リスト方式で削除漏れが発生した
- 生成後に手動編集した
- リリース作業ディレクトリを再利用した

対応:

- そのZIPをリリースしない
- 新しい空ディレクトリから許可リスト方式で再生成する
- 許可外ファイル検査をリリース失敗条件にする
- 入力SHA-256、生成スクリプト、許可リスト、出力マニフェストを保存する
- 再生成した2つのツリーでファイル一覧とハッシュを比較する

---

## GPIO直結パッシブブザーPoCの上限と停止条件

対象は`12085P`をD6/A2（PC4 / TIM1_CH4）へ追加部品なしで接続する主催者用PoCに限定する。

上限:

```c
#define MAX_TONE_DURATION_MS  2000u
#define MAX_TOTAL_TONE_MS     2000u
#define DIRECT_DUTY_DIVISOR   2u
#define DIRECT_COOLDOWN_MS    5000u
```

次を確認する。

- ホスト側とファームウェア側の値が一致する
- `make status`でデューティ除数`2`、最大総発音時間`2000`、クールダウン`5000`が表示される
- 2,001msを指定したコマンドが拒否される
- クールダウン中のPLAYが拒否される
- STOPで直ちにPWMが停止する

発熱、異臭、USB切断、再列挙、リセット、音の急変、STOP不能が発生した場合はUSBを直ちに外す。

5V・50%・2秒で明確な問題がなかったという利用者実機報告はあるが、電流、PC4端子電圧、
誘導性スパイク、温度、反復耐久は未確認である。参加者向け標準回路へは採用しない。



## 41. `rv003usb requires FUNCONF_SYSTICK_USE_HCLK 1`

代表例:

```text
#error "RV003USB requires #define FUNCONF_SYSTICK_USE_HCLK 1; see funconfig.h"
```

対応:

```c
#define FUNCONF_SYSTICK_USE_HCLK 1
```

定義だけ変更すると時間処理が8倍ずれる実装がある。サンプリング周期、振動時間、タイムアウトをクロック設定から換算していることを確認する。

## 42. `Error: Could not open flash`と空の書き込みファイル名

実行ログが次の場合:

```text
minichlink -c 0x1209b803 -w  flash -b
Error: Could not open flash
```

`-w`直後のファイル名が空である。`FLASH_COMMAND := ... $< ...`のように自動変数を即時展開していないか確認する。

確認済み修正:

```make
FLASH_COMMAND = $(MINICHLINK)/minichlink -c 0x1209b803 -w $(TARGET).bin flash -b
```

`shasum: not found`が同時に出ても、CH32V003検出後に`Could not open flash`となった主因は空のファイル名である可能性が高い。

## 43. `ModuleNotFoundError: No module named 'hid_device'`

演習内の`host/hid_device.py`が存在しても、Windows Embedded Pythonの隔離構成ではスクリプトディレクトリが探索対象に入らない場合がある。

エントリーポイントで自身のディレクトリを`sys.path`先頭へ追加する。参加者に`PYTHONPATH`やシステムPythonへの切替を要求しない。

## 44. ポテンショメーターADC値とポインター段階がふらつく

切り分け:

```text
make adc-monitor
```

確認:

- ポテンショメーターを静止して5秒以上観察
- `window=min..max`と`span`を記録
- モーター停止中にも値が大きく揺れるか
- 段階境界でだけ往復するか

配線確認:

- D1/A0とD0/A1の0.1µFがGNDへ接続
- 68kΩと100kΩの分圧が両チャンネルで同じ
- 5VワイパーをADCへ直結していない
- 配線を短くし、ADCコンデンサーをボード側へ近づける
- モジュールVCC-GND間の100µFの極性
- USBハブを外してPCへ直結

v1.0.8の確認済み対策:

- チャンネル切替後2回破棄
- 16サンプルから最大・最小を除外した平均
- 5点中央値
- 低域フィルタ
- 3カウントの報告値デッドバンド
- 12カウントの段階ヒステリシス
- 隣接段階を3サンプル連続で確定
- モーター駆動中と停止後50msのADC停止

古いファームウェアのままホスト側だけ更新しても改善しない。`make clean`、`make flash`を実行する。

## 45. stale restore stateが残っている

アプリ起動時に次が表示される場合:

```text
[UIAP] A stale restore state was found; restoring it first.
```

前回の異常終了でWindowsポインター設定の復元stateが残っている。v1.0.7以降は起動前に自動復元する。手動確認する場合:

```text
make restore
make cursor-test
```

復元stateを参加者向けZIPへ含めない。


## 46. `[UIAP-E103] 開発キットの展開先フォルダーを使用できません`

### 症状

`start-uiap.cmd`の起動直後、`setup`、または`doctor`で次を表示して停止する。

```text
[UIAP-E103] 開発キットの展開先フォルダーを使用できません。
```

### まず現在の場所を確認する

#### 実際に非対応の例

```text
C:\UIAP Test\uiap-devkit-win64
C:\開発\uiap-devkit-win64
\\server\share\uiap-devkit-win64
```

空白、日本語・全角文字、その他の非ASCII文字、UNCパスを含むため、現行方針では非対応である。

#### 本来は使用できる例

```text
C:\uiap\uiap-devkit-win64
C:\pj\uiap-devkit-win64
C:\pj\xpfes2026\uiap-devkit-win64
```

各フォルダー名がASCII・空白なしであれば、複数階層でも使用できる。

### 実際に非対応パスだった場合

1. 現在のコンソールを閉じる
2. Devkitフォルダー全体を次のような場所へ移動する

```text
C:\uiap\uiap-devkit-win64
```

または:

```text
C:\pj\uiap-devkit-win64
```

3. 移動先の`start-uiap.cmd`を実行する
4. 次を実行する

```text
setup
doctor
```

### 有効なパスなのに表示された場合

`C:\pj\xpfes2026\uiap-devkit-win64`のような有効パスで表示された場合、フォルダー名が原因ではない。

Devkit `0.4.3-test11`には、パス検査用正規表現の回帰不具合がある。

問題のある形式:

```powershell
$asciiSafePattern = '^[A-Za-z]:\[A-Za-z0-9_.\-]+$'
```

問題点:

- `\[`がWindowsの区切り文字ではなく、正規表現上のリテラル`[`として解釈される
- 複数階層を繰り返す構造がない
- 通常の有効なWindowsパスまで拒否する

対応:

1. フォルダーを別のASCIIパスへ移動して回避しようとしない
2. `VERSION`を確認する
3. `0.4.3-test11`を使用しない
4. パス判定を修正したDevkitへ切り替える
5. 参加者にMakefileやPowerShellを編集させない

### 恒久対策

パス判定を`scripts/path-check.ps1`へ集約する。

```text
start-uiap.cmd
  └─ scripts/path-check.ps1
setup.ps1
  └─ scripts/path-check.ps1
doctor.ps1
  └─ scripts/path-check.ps1
```

正規表現を使用する場合の概念例:

```powershell
$asciiSafePattern = '^[A-Za-z]:\\[A-Za-z0-9._-]+(?:\\[A-Za-z0-9._-]+)*$'
```

修正版では次を実機確認する。

- `C:\uiap\uiap-devkit-win64`を許可
- `C:\pj\uiap-devkit-win64`を許可
- `C:\pj\xpfes2026\uiap-devkit-win64`を許可
- 空白パスを拒否
- 全角パスを拒否
- UNCパスを拒否
- エラー本文を日本語表示

### 行わない対応

- Makefileへ場当たり的に引用符を追加する
- 8.3短縮名へ手動変換する
- `subst`を参加者へ実行させる
- Devkitの一部だけを別フォルダーへ移す
- 有効パスでの誤検出を参加者の展開ミスとして扱う

## 29. macOS演習02で`make list`が`Matching devices: 0`

### 状態

ファームウェアのビルドと書き込みは成功しているが、次になる。

```text
Matching devices: 0
```

### 切り分け

```sh
ioreg -p IOUSB -l -w 0
hidutil list
```

`ioreg`に`1209:C004`があり、`hidutil list`またはネイティブホストにない場合は、USB Device列挙とIOHID列挙の間で停止している。

`0.1.9-test10a`以前の演習02には、Device Descriptorの`bDeviceClass = 3`とHID制御要求不足が残っていた。macOSではUSB Deviceとして見えてもIOHIDデバイスを生成しない場合がある。

### 対応

- `0.2.0-test11`以降を使用する
- Device Descriptorのクラス3フィールドが`0`であることを確認する
- HIDクラスはInterface Descriptorで宣言する
- 必要な`GET_REPORT`、`GET_IDLE`、`SET_IDLE`を処理する
- Productが`UIAP Rotary Cursor macOS Test11`以降であることを確認する

Windowsで動作したことだけを根拠にmacOS合格としない。

## 30. `Cursor-scale API: PASS current=0.00`または`UIAP-CURSOR-E207`

### 代表表示

```text
Cursor-scale API: PASS current=0.00
Original pointer scale: 0.00
[UIAP-CURSOR-E207] Could not set pointer scale 0.50.
[UIAP-CURSOR-E205] No saved pointer size is available.
```

### 原因

`0.2.0-test11`のネイティブホストは、非公開`CGSGetCursorScale`／`CGSSetCursorScale`のスカラー型を64bit型として扱った。実際の環境が32bit `float` ABIの場合、正常値を`0.00`相当へ誤読し、setterにも不正な値を渡す。

`E205`は、誤読した`0.00`が有効な復元値ではないために発生する二次エラーである。最初の変更に失敗している場合、通常はmacOS設定自体は変更されていない。

### 対応

- test11では`make app`を再実行しない
- `0.2.1-test12`以降へ更新する
- 古い無効状態ファイルがある場合は削除する

```sh
rm -f "$UIAP_DEVKIT_ROOT/.state/02_rotary_cursor_size.original-scale"
```

更新後、次の順に確認する。

```sh
make app-dry-run
make host-doctor
make app
```

`make host-doctor`は、ABI判定、現在値読取り、同値書込み、再読取りが成功した場合だけPASSにする。`current=0.00`、NaN、範囲外値をPASSにしない。

## 31. test12でカーソル変更後に復元されない

### 正常時

`make app`を`Ctrl+C`で終了すると、起動前のカーソル倍率へ戻り、復元成功表示が出る。

### 確認

```sh
make restore
```

### 切り分け

- `.state/02_rotary_cursor_size.original-scale`が存在するか
- 保存値が有限で妥当な範囲か
- `make host-doctor`がPASSか
- 非公開APIの読取り・書込み・再読取りが成功するか
- 別のアプリやシステム設定が同時にポインターサイズを変更していないか

復元成功後は状態ファイルを削除する。状態ファイルがない場合と、API書込みに失敗した場合を別のエラーとして扱う。

macOS 26.5.2では`Ctrl+C`終了時復元を利用者実機確認済みである。USB切断時復元は未確認なので、問題が発生した場合はログを保存し、手動でシステム設定のポインターサイズを確認する。

## 32. Windowsの大容量ダウンロード

### 32.1 進捗バーが表示されない

確認:

- `start-uiap.cmd`から起動した専用Command Promptか
- `setup`コマンドを実行したか
- PowerShellで`curl`や`Invoke-WebRequest`を直接実行していないか
- `%SystemRoot%\System32\curl.exe`が存在するか
- `doctor`でcurl.exeがPASSか

Devkitの内部URLをブラウザへコピーして手動取得する前に、`report`でログを保存する。

### 32.2 `[UIAP-E120] Windows標準のcurl.exeが見つかりません`

Windows 11 x64のサポート対象環境か確認し、Windows Updateを適用する。別サイトから任意のcurl.exeをダウンロードしてDevkitへ置かない。主催者は対象Windowsビルドとセキュリティポリシーを記録する。

### 32.3 `[UIAP-E121] ダウンロードに失敗しました`

表示されたcurl終了コードで切り分ける。

| 終了コード | 主な意味 | 確認 |
|---:|---|---|
| 6 | ホスト名を解決できない | DNS、ネットワーク、URL |
| 7 | 接続できない | ファイアウォール、プロキシ、配布元障害 |
| 28 | タイムアウト | 回線、VPN、プロキシ、再実行 |
| 33 | Range再開に非対応 | Devkitが`.part`を削除して先頭再取得するか |
| 35 | TLS接続失敗 | TLS検査、プロキシ、日時 |
| 60 | 証明書検証失敗 | OS証明書、日時、企業プロキシ |

終了コード6、7、28、35、60では`.part`を保持し、原因解消後に同じDevkitで`setup`を再実行する。

### 32.4 `[UIAP-E122] SHA-256が一致しません`

不一致ファイルは`.bad-<timestamp>`へ隔離される。正式キャッシュへ手動改名しない。

確認順序:

1. Devkit版と対象コンポーネントを確認する
2. URL、保存ファイル名、アーカイブ形式、期待SHA-256の組を確認する
3. HTMLエラーページ、プロキシ書換え、ディスク異常を除外する
4. ロックの誤りが判明した場合は、修正版Devkitまたは正式ホットフィックスを使用する

`0.5.2-test15`でch32fun取得時に発生する場合は、ZIPとtar.gzのSHA-256混用による既知不具合である。`0.5.3-test16`またはtest16ホットフィックスを適用し、隔離済みファイルを削除せずに`setup`を再実行する。test16は隔離ファイルを現在の期待値で再検証し、一致する場合だけ採用する。

ハッシュ固定の規則は`20_BUILD_RULES.md`、ch32fun固有値は`15_CH32FUN_SUBSET_RULES.md`、実機記録は`70_VALIDATION_RESULTS.md`を参照する。

### 32.5 `.part`が残っている

中断または通信失敗を示す。正常な復旧手順:

```text
setup
```

`.part`を正式ZIPへ手動改名しない。複数版Devkit間で`.part`をコピーしない。再開後も繰り返し失敗する場合は`report`を作成し、curl終了コード、ファイルサイズ、ネットワーク条件を記録する。

## 33. `start-uiap.cmd`の案内後に`cmd.exe`が見つからず閉じる

代表表示:

```text
'cmd.exe' is not recognized as an internal or external command,
operable program or batch file.
```

### 原因

`0.5.1-test14`は、Devkit用PATHを設定した後に相対名`cmd.exe`を実行していた。System32をPATHから解決できない環境では、パス検査と案内表示は成功しても専用Command Promptへ移行できない。

### 対応

1. test14のウィンドウを閉じる
2. test14へファイルを上書きしない
3. `0.5.2-test15`を新しい空フォルダーへ展開する
4. `start-uiap.cmd`をダブルクリックする
5. 案内後もウィンドウが残ることを確認する
6. `doctor`を実行し、`cmd.exe`、Windows PowerShell、PATHのSystem32保持がPASSになることを確認する

PowerShellから直接Devkitを継続利用することを参加者向け標準回避策にしない。

## 2026-08-01 `[UIAP-E240]`が表示される

`0.5.x-test15/test16`の`01_macro_keyboard`と`02_rotary_cursor_size`は、未統合コードを誤配布しないためのプレースホルダーだった。

`0.6.0-test17`ではプレースホルダーを除去する。test17を使用しているのに`UIAP-E240`が表示される場合は、旧版との混在を疑う。

対応:

1. `VERSION`を確認する
2. 現在のコンソールを閉じる
3. test17を新しい空フォルダーへ完全に展開する
4. `start-uiap.cmd`から起動する
5. `setup`、`doctor`を実行する
6. 対象演習で`make clean`、`make`を実行する

## rv003usbソース取得で停止する

test17では固定コミットのRaw URLから次を取得する。

```text
rv003usb/rv003usb.S
rv003usb/rv003usb.c
rv003usb/rv003usb.h
LICENSE
```

確認項目:

- GitHubのRawドメインへHTTPS接続できる
- セキュリティソフトが`.S`、`.c`、`.h`を隔離していない
- `workspace/deps/rv003usb/UPSTREAM_COMMIT`が期待コミットと一致する
- `SOURCE_FILES.sha256`が生成されている

取得途中で失敗した場合は、他の正常なランタイムを削除せず`setup`を再実行する。

## 2026-08-01 `make flash`でminichlinkのUsageが表示される

代表例:

```text
...minichlink -c 0x1209b803 -w   -b
Usage: minichlink [args]
make: *** [...: cv_flash] Error 255
```

### 判定

ビルドがFLASH/RAM表示とBIN生成まで完了し、minichlinkが`1209:B803`とCH32V003を検出している場合、コンパイラ、rv003usb、USBブートローダー検出の失敗ではない。`-w`へ渡す書き込みファイル名が欠落している。

`0.6.0-test17`では、`FLASH_COMMAND := ... $< ...`の単純展開代入により、自動変数`$<`がルール実行前に空へ展開された。

### 対応

1. test17で同じ`make flash`を繰り返さない
2. `0.6.1-test18`へ更新する
3. `doctor`で3演習の`make -n flash`検査がPASSになることを確認する
4. 対象演習で`make clean`、`make flash`を再実行する

正常なdry-run例:

```text
minichlink -c 0x1209b803 -w macro_keyboard.bin flash -b
```

## 2026-08-01 Newlib診断の誤判定

`doctor`が次を表示しても、実際のコンパイル行に`-I/usr/include/newlib`がない場合は、test17の診断誤判定である。

```text
[FAIL] ch32fun.mkに実効Newlib依存が残っています
```

原因は、実効CFLAGSではなく未使用の`NEWLIB?=/usr/include/newlib`定義まで検索したことにある。test18では必須演習の`make -n build`出力だけを判定する。上流`ch32fun.mk`の既定値を手作業で削除して回避しない。

## 2026-08-01 test18の`make app`で`[WinError 6] ハンドルが無効です`

### 観測結果

`uiap-devkit-win64` `0.6.1-test18`の`02_rotary_cursor_size`で次を確認した。

- 書き込みと`1209:C004`列挙: 成功
- `make app-dry-run`のCW／CCW受信: 成功
- `make app`: 対象デバイス1台と起動前サイズ80を表示
- 最初のポインターサイズ反映時に`[WinError 6] ハンドルが無効です`で終了

この条件では、USB HID、hidapi、エンコーダー入力ではなくWindows設定変更処理を切り分ける。

### 原因

test18のホストアプリが、レジストリ更新後のカーソル再読込に`SPI_SETCURSORS (0x0057)`を使用した。プロジェクト内の`03_pot_cursor_haptic` v1.0.6でも同じエラーを確認しており、v1.0.7で同呼出しを除去して修正済みだった。test18はこの既知不具合を再導入した回帰とする。

### 修正版

`0.6.2-test19`では次を行う。

- `SPI_SETCURSORS`を使用しない
- 過去のWindows 11 x64実機PoCで確認した未文書化アクション`0x2029`を使用する
- `CursorBaseSize`と`Software\Microsoft\Accessibility\CursorSize`を保存・復元する
- test17／test18形式の保存状態を読み取る
- 前回異常終了の保存状態をアプリ起動前に自動復元する
- HID入力と分離した`make cursor-test`を提供する

### test19適用後の確認順

```text
cd /d "%UIAP_WORKSPACE%\exercises\02_rotary_cursor_size"
make restore
make cursor-test
make app
```

`make restore`が保存状態なしを表示した場合は、`make cursor-test`へ進む。保存状態ファイルを手作業で削除しない。

### test19での解消確認

Windows 11 x64の利用者実機で`0.6.2-test19`を確認し、次が成功した。

- `make flash`で`rotary_cursor_size.bin`を書き込み
- `1209:C004`を1台検出
- CW／CCWを受信
- ポインターサイズを16単位で増減
- `Ctrl+C`で終了
- 起動前サイズ80へ復元

正常終了時の代表表示:

```text
Stopping.
Restored pointer size: 80
```

したがって、test18の`[WinError 6] ハンドルが無効です`はtest19で解消確認済みとする。test19で同じエラーが再発する場合は、旧test18ファイルとの混在、`VERSION`、`host/cursor_size_host.py`の更新状態を確認する。

なお、USB切断、強制終了後の`make restore`、別Windows PCでは引き続き別途検証する。

<!-- Source: 70_VALIDATION_RESULTS.md -->

# 検証結果

更新日: 2026-08-01

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
workspace/exercises/02_rotary_cursor_size/host/cursor_size_host.py
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
```

### 情報源

既存の`90_DECISIONS.md`から転記した検証結果である。

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

配線:

```text
D6/A2 → PC4 → TIM1_CH4
```

`1209:D003`はPoC用一時値である。

### 未確認

- macOS Apple Silicon実機
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
| macOS Apple Silicon | 必須演習3本合格。ロータリーカーソルはCW／CCW、サイズ変更、`Ctrl+C`復元を確認 |
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

<!-- Source: 90_DECISIONS.md -->

# 決定履歴

この文書は、決定事項、検討中事項、未確認事項、却下事項を区別するために使用する。

新しい決定は日付付きで追記する。過去の記録を無断で書き換えず、変更理由を残す。

> **現行仕様の読み方:** 2026-07-25以降のWindows xPackネイティブ決定、および2026-08-01の配布Devkit最終方針を現行仕様とする。これ以前のMSYS2、最終オフライン版、macOS 15対応に関する記述は、当時の検証履歴または旧方針として保持する。

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
- 主催者用PoCは`workspace/poc`
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

必要なら旧PoCを標準位置へ移動し、Makefileの依存参照を`UIAP_WORKSPACE`ベースへ変更する。参加者向け配布版へ含めるかは別途判断する。

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
- `workspace/poc`を参加者向け配布版へ含めるか
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
workspace/exercises/02_rotary_cursor_size/host/cursor_size_host.py
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
- macOS版にもPythonとhidapiを含める。`02_rotary_cursor_size`の現行ネイティブarm64ホスト自体がPython/hidapiへ依存しないこととは区別する。
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
