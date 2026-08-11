# 配布パッケージ作成・リリースチェックリスト

更新日: 2026-08-05

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

### 8.1 USB HID事前診断

`workspace/preflight`について、Windows版とmacOS版の両方で次を確認する。

- README、Makefile、`preflight_hid.c`、`usb_config.h`、`host/preflight_hid.py`が配布ZIPに存在
- `.bin`、`.elf`、`.hex`、`.lst`、`.map`、生成された`funconfig.h`が配布元と配布ZIPに存在しない
- `make clean`、`make`、`make size`が成功
- `make flash`後にVID `1209`、PID `D003`、製品名`UIAP HID Preflight`として列挙
- `make preflight`がUSB列挙、双方向通信、プロトコル、ファームウェア、ボード名、MCU IDを確認
- 成功時の終了コードが`0`、失敗時が非ゼロ
- ファームウェアとホスト診断の期待バージョンが一致
- 診断用UIAPduinoが0台または複数台の場合に、明確なエラーで終了

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

- 指定の5ピンエンコーダーモジュールを使用
- `01_macro_keyboard`ではGND→GND、KEY→D5 / PC3の2本だけを接続
- S1、S2、5Vを接続しなくても期待文字列を入力
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

指定のセンタースイッチ付きモジュールを使用する場合:

`01_macro_keyboard`の2本へ、S1、S2、5Vの3本を追加していることを確認する。

| UIAPduino | モジュール |
|---|---|
| GND | GND |
| D8 / PC6 | S1 |
| D9 / PC7 | S2 |
| D5 / PC3 | KEY |
| 5V | 5V |

確認項目:

- `02_rotary_cursor_size`のファームウェアがKEYを読み取らない
- UIAPduinoのマイクロコントローラー電源が初期状態の5V設定
- 5V電源とGNDが正しい
- 基板表記のGND/S1/S2/KEY/5Vが配線表と一致
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

配布ZIP作成コマンドが上記の版番号不一致を検出して失敗することを確認する。タグ公開時は、Windows版とmacOS版の両方のビルドが成功するまでReleaseを公開しない。

## 2026-08-08 Devkit 0.1.1 配布修正

Devkit `0.1.0`のWindows版は、`VERSION=0.1.0`に対してbootstrap lockが`0.1.0-dev`のまま公開され、`setup`が`UIAP-E133`で停止したため使用しない。`0.1.1`では次をリリース条件とする。

- [x] `VERSION`とWindows bootstrap lockが`0.1.1`で一致
- [x] `VERSION`とmacOS bootstrap lockが`0.1.1`で一致
- [x] ZIP作成前の版番号整合性検査を追加
- [x] `--version`によるZIP名と同梱メタデータの不一致を拒否
- [x] 両OSの配布ZIPを作成し、同梱版番号とSHA-256を検証

ch32funの具体的な入力値は`15_CH32FUN_SUBSET_RULES.md`を参照し、このチェックリストへ重複記載しない。

## 2026-08-01 Windows test17追加検査

`uiap-devkit-win64` `0.6.0-test17`では、次を確認する。

- [ ] `VERSION`と`bootstrap.lock.json`が`0.6.0-test17`で一致
- [ ] `01_macro_keyboard`のプレースホルダーがなく、必要ソースが揃っている
- [ ] `01_macro_keyboard`の`macro_keyboard.c`、`usb_config.h`、`host/hidcheck.py`が演習直下の共通実装である
- [ ] `01_macro_keyboard`に`win/`、`mac/`の重複ソースが残っていない
- [ ] `00_onboard_led_blink`と`02_rotary_cursor_size`のファームウェアも演習直下の共通実装である
- [ ] `02_rotary_cursor_size`のOS固有コードは`host/win`と`host/mac`だけに限定されている
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
