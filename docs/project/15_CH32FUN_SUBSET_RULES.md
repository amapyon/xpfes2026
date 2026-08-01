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

