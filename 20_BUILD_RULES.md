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

参加者向け最終配布版では、追加インストール、管理者権限、当日のネットワーク接続を前提にしない。オンライン・ブートストラップ型Devkitを検証用に使用する場合は、最終オフライン配布版と区別し、用途と未検証範囲を明記する。

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

オンライン・ブートストラップ型の検証版では、取得URLとSHA-256を固定し、取得済みファイルを再利用できる構成にする。

最終参加者向け配布版では、ワークショップ中に最新版を取得しない。当日の`pip install`、`pacman -S`、Homebrew、Git cloneを標準手順に含めない。

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

オンライン検証版の`setup`は固定URLとSHA-256で主要ツールを取得する。最終版では展開済みランタイムを同梱し、ネットワーク切断状態で同じコマンドが動くことを確認する。

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

オンライン主催者検証版で固定コミットのRaw URLからソースを取得する場合、URLへ完全コミットIDを含め、取得した各ファイルのSHA-256を記録する。最終リリースでは、その実測値を期待値として固定し、取得後検証またはオフライン同梱へ移行する。

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
