# トラブルシューティング指針

更新日: 2026-07-31

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
- ネットワーク切断状態での成功

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

