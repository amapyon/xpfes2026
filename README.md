# XP祭り2026 プロジェクト指示ファイル

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
| `99_FULL_PROJECT_GUIDE.md` | 全文統合版 |

通常は `90_DECISIONS.md` を最初に参照し、次に作業分野に対応する文書を参照する。


## 2026-07-31 macOS test12検証と必須演習

- ワークショップの必須演習を次の3本とする
  - `00_onboard_led_blink`
  - `01_macro_keyboard`
  - `02_rotary_cursor_size`
- macOS Apple Silicon向けの最新主催者検証版は`uiap-devkit-macarm64` `0.2.1-test12`である
- macOS 26.5.2、Apple Silicon arm64、Rosetta不使用で、必須演習3本の実機動作を確認した
- `01_macro_keyboard`は、初回接続時のキーボード設定アシスタントを前の画面へ戻って「終了」で閉じた後、`AbCdE`入力、長押し抑止、再押下、キー解放、USB再接続を確認した
- test9のHID Device Descriptor不具合とNewlib検査漏れはtest10／test10aで修正した
- test11で`02_rotary_cursor_size`のUSB・IOHID列挙とCW／CCW受信を確認したが、非公開カーソルAPIのスカラーABI不一致により現在値を`0.00`と誤読し、変更と復元に失敗した
- test12ではカーソル倍率APIの`float32`／`float64` ABIを実行時判定し、不正値を保存しない処理、同値書込み自己診断、変更後と復元後の再読取り検証を追加した
- test12で、エンコーダーによるCW／CCW入力、カーソルサイズ変更、`Ctrl+C`終了時の起動前サイズ復元が想定どおり動作したとの利用者実機報告を確認した
- USB切断時復元、別Mac・別ユーザー、最低対応macOS、非公開APIの将来互換性、最終許可リスト版`ch32fun`、`rv003usb`入力SHA-256正式固定、ネットワーク切断状態、最終オフラインZIPは未確認である

## 2026-07-29 macOS Apple Silicon Devkit検証

- `uiap-devkit-macarm64`の主催者検証版`0.1.7-test8`で、オンライン`setup`からLチカの物理動作までをApple Silicon実機で確認した
- 検証環境はmacOS 26.5.2、arm64ネイティブ、Rosetta 2不使用である
- GNU Make 4.4.1、xPack GNU RISC-V Embedded GCC 14.2.0-3、固定コミットの`ch32fun`と`rv003usb`をDevkit内から使用した
- `build-minichlink`で、固定コミットの`ch32fun`に含まれる`minichlink`とlibusb 1.0.29を使い、arm64版書き込みツールをローカル生成した
- libusbは静的リンクし、生成した`minichlink`に`/opt/homebrew`、`/usr/local`、開発者ホーム配下の動的ライブラリ依存がないことを確認した
- ローカル生成した`minichlink`単体の隔離属性を除去し、アドホック署名と署名検証を行う処理を自動化した
- `doctor`は`PASS=32 WARN=1 FAIL=1`で、残る項目は最終`ch32fun`許可リストと同梱Python・hidapiである
- `make flash`でUSBブートローダー`1209:B803`、CH32V003、書き込み、ブートを確認し、基板上LEDの0.2秒点灯・0.8秒消灯を物理確認した
- 現行版はオンライン初期化型の主催者検証版であり、参加者向け最終オフライン版ではない
- Devkit内Python・hidapi、HID演習、ネットワーク切断状態、別Mac・別ユーザー、最終署名・公証方針は未確認または未決定である
## 2026-07-26 更新概要

- `workspace/exercises/03_pot_cursor_haptic` v1.0.8のWindows 11 x64実機結果を反映
- RV09 B10Kポテンショメーター、Vendor-defined HID、Windowsポインターサイズ、振動モーターモジュールの統合動作を記録
- ADCの外れ値除去、中央値、低域フィルタ、デッドバンド、段階ヒステリシス、確定待ち、モーター停止後待機を記録
- ワークショップ必須演習への採用、正式VID:PID、macOS相当実装は未決定

## 2026-07-26 展開先パス制約

- Windows版Devkitは、ローカルドライブ上のASCII・空白なしパスを標準とする
- パスは複数階層を許可し、各フォルダー名に半角英数字、ドット、ハイフン、アンダースコアを使用できる
- `C:\uiap\uiap-devkit-win64`、`C:\pj\uiap-devkit-win64`、`C:\pj\xpfes2026\uiap-devkit-win64`はいずれも有効な例とする
- 空白、全角文字、その他の非ASCII文字、UNCパスを含む展開先だけを`UIAP-E103`で拒否する

## 2026-07-26 展開先パス検査の回帰不具合

- Devkit `0.4.3-test11`が、有効な`C:\pj\xpfes2026\uiap-devkit-win64`を`UIAP-E103`で拒否することを利用者実機で確認
- 原因は、パス検査用正規表現がWindowsのバックスラッシュと複数階層を正しく表現していない実装ミス
- `0.4.3-test11`はWindows版リリース候補として使用しない
- パス判定は`scripts/path-check.ps1`へ集約し、`setup.ps1`と`doctor.ps1`は共通判定を呼び出す
- 参加者向け日本語メッセージの方針は維持する
- 修正版は、有効な複数階層ASCIIパスでの成功と、空白・全角・UNCパスでの拒否を実機確認してから配布する


## 2026-07-27 演習ディレクトリへの移動方法

- `sample`、`macro`、`blink`など、演習フォルダーへ移動するためのトップレベルコマンドは廃止する
- `cursorapp`、`cursorlist`、`cursorrestore`など、特定演習だけを操作するトップレベルコマンドも廃止する
- 受講者は`cd`コマンドで対象の`workspace/exercises/<exercise-name>`へ移動する
- 演習内では`make`、`make flash`、`make app`、`make list`、`make restore`など、その演習のMakefileターゲットを使用する
- Devkit共通のトップレベルコマンドは`setup`、`doctor`、`versions`、`report`などに限定する
- `cursorstore`は標準コマンド名として採用しない。復元操作は演習内の`make restore`へ統一する
