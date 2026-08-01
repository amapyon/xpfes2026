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
| `01_macro_keyboard` | 必須。5ピンエンコーダーモジュールのKEYによるUSB HIDキーボード |
| `02_rotary_cursor_size` | 必須。同じモジュールのS1/S2とOS別ホストアプリ |
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
