# macOS版トラブルシューティング

## `start-uiap.command`を開けない

表示例:

```text
Appleは“start-uiap.command”にMacに損害を与えたり、プライバシーを侵害する可能性のあるマルウェアが含まれていないことを検証できませんでした。
```

原因:

- ZIPをブラウザから取得したため隔離属性が付いている
- このテスト版はApple Developer IDで署名されていない
- Appleによる公証を行っていない

対応:

1. 警告画面で`完了`を押す
2. Appleメニュー > `システム設定` > `プライバシーとセキュリティ`を開く
3. `セキュリティ`欄の`このまま開く`を押す
4. ログインパスワードまたはTouch IDで承認する
5. 再確認画面で`開く`を押す

`ゴミ箱に入れる`を押した場合は、ZIPから再展開します。

Devkit全体への`xattr -dr com.apple.quarantine`や、`sudo spctl --master-disable`は標準復旧手順にしません。

## `このまま開く`が表示されない

- 警告を出してから時間が経過している可能性があります
- もう一度`start-uiap.command`をダブルクリックして警告を表示します
- `完了`を押した直後に`プライバシーとセキュリティ`を開きます
- 組織管理Macでは管理者ポリシーにより個別許可できない場合があります

## 起動後に別のスクリプトで警告される

0.1.1-test2以降では、補助スクリプトを`/bin/sh`から読み込む構成へ変更しています。警告対象のファイル名とDevkitの`VERSION`を記録してください。

## `cd: .../Downloads/workspace: No such file or directory`

表示例:

```text
start-uiap.command: line 18: cd: /Users/<user>/Downloads/workspace: No such file or directory
```

原因:

- `0.1.1-test2`の`env.sh`が、sourceされたファイル内の`$0`を`env.sh`自身のパスとして誤って使用していました
- 実際の`$0`は`start-uiap.command`を指すため、Devkitルートを1階層上の`Downloads`と誤判定していました

対応:

1. `VERSION`を確認します
2. 古いテスト版の場合は`0.2.2-test13`へ置き換えます
3. ZIPを新しい空のディレクトリへ完全に展開します
4. `start-uiap.command`を起動します

`0.1.9-test10a`では、`start-uiap.command`が自分の配置ディレクトリを`UIAP_DEVKIT_ROOT`として明示し、`env.sh`はその値を使用します。

## `UIAP_WORKSPACE is not set`

FinderでDevkit最上位の`start-uiap.command`から開き直します。任意のTerminalから直接`make`を実行しません。

## `make`が見つからない

```sh
versions
```

このテスト版は`setup`でDevkit内へ配置したGNU Makeを使用します。システムの`/usr/bin/make`へフォールバックしません。

## `minichlink`が利用できない

`minichlink`がプレースホルダーの場合は、主催者用Macで`build-minichlink`を実行してから`doctor`を再実行します。

## 当日の切り分け

1. Devkitの`VERSION`を確認
2. `doctor`を実行
3. `versions`を実行
4. 生成された最初のエラーを保存
5. `report`を実行
6. Macの機種、macOSバージョン、CPUアーキテクチャを記録

## `[UIAP-E202] Bundled GNU Make is not installed`

`0.1.7-test8`以降は`/usr/bin/make`やXcode Command Line Toolsへ依存しません。Devkit起動後に次を実行します。

```sh
setup
```

`setup`はmacOSのバージョンに対応するGNU Make 4.4.1 arm64ボトルを固定SHA-256で取得し、`runtime/build-tools/bin/gmake`へ配置します。

再確認:

```sh
doctor
versions
```

SHA-256不一致、arm64以外、起動失敗、`/opt/homebrew`または開発者ホームへの動的ライブラリ依存を検出した場合は導入を中止します。


## `make flash`が`Killed: 9`で停止する

確認済み原因の一つは、ローカル生成した`runtime/bin/minichlink`にブラウザ由来の`com.apple.quarantine`が残っていることである。

確認:

```sh
xattr -l "$UIAP_RUNTIME/bin/minichlink"
codesign --verify --verbose=4 "$UIAP_RUNTIME/bin/minichlink"
```

`com.apple.quarantine`が表示された場合、手作業でDevkit全体を再帰処理せず、`build-minichlink`を再実行する。test8以降は生成した`minichlink`単体の隔離属性除去、アドホック署名、署名検証を自動実行する。


## test10: `build-host-tools`が失敗する

確認:

```sh
xcrun --sdk macosx --find clang
xcrun --sdk macosx --show-sdk-path
```

主催者検証用MacだけにApple Command Line Toolsが必要です。参加者向け最終版ではビルド済みバイナリを同梱する方針です。

## test10: `[UIAP-E236] Cursor host self-test failed`

現在のmacOSで`CGSGetCursorScale`または`CGSSetCursorScale`を解決できていません。これらは非公開APIです。このエラーを回避して参加者向けに配布せず、OSバージョンと完全なログを記録してください。

## test10: `make list`でデバイスが0台

- `02_rotary_cursor_size`を書き込んだか
- 書き込み後に通常アプリケーションとして再列挙したか
- UIAPduinoを1台だけ接続しているか
- USBハブを外してMacへ直結したか
- データ通信対応ケーブルか

期待するアプリケーションVID:PIDはPoC用の`1209:C004`です。

## test10: `make app`でポインターサイズが変わらない

先に次を実行します。

```sh
make app-dry-run
```

CW/CCWが出る場合はHID経路が成功し、カーソルAPI側の問題です。CW/CCWが出ない場合は配線、エンコーダー方向、HID列挙を切り分けます。

## test10: 異常終了後にポインターサイズが戻らない

```sh
make restore
```

状態ファイルがない、または復元に失敗する場合は、システム設定の「アクセシビリティ」→「ディスプレイ」→「ポインタのサイズ」で手動復旧します。


## test10: USBツリーには出るが`hidutil list`に出ない

次を取得します。

```sh
ioreg -p IOUSB -l -w 0 > /tmp/uiap-usb.txt
hidutil list > /tmp/uiap-hid.txt
```

`ioreg`で`bDeviceClass = 3`の場合はtest9以前のファームウェアです。test10を`make clean`から再ビルドして書き込みます。test10の期待値は`bDeviceClass = 0`です。

Productが`UIAP Macro Keyboard Test`、Serialが`TEST3-001`の場合も旧ファームウェアです。test10はProduct `UIAP Macro Keyboard macOS Test10`、Serial `TEST10-001`です。

`bDeviceClass = 0`でも`hidutil list`へ出ない場合は、`doctor`全文、`ioreg`該当部分、`hidutil list`、macOSバージョンを保存します。USB抜き差し後も同じか確認し、別ポートまたはPC直結で再試行します。

## test10: `doctor`はNewlib除去PASSだがコンパイル行に`/usr/include/newlib`が出る

これは不合格です。test10の`doctor`はソース文字列だけでなく、各必須演習の`make -n build`出力を検査します。

```sh
setup
doctor
```

改善しない場合は、`workspace/deps/ch32fun/ch32fun/ch32fun.mk`に`-I$(NEWLIB)`が残っていないか確認します。手作業では修正せず、test10の`setup`を再実行します。

## test10: `doctor`がNewlib FAILだがdry-runはPASS

`0.1.9-test10`では、上流`ch32fun.mk`に残る未使用の既定値
`NEWLIB?=/usr/include/newlib`を再帰検索が検出し、実際の`-I$(NEWLIB)`が
除去済みでもFAILにする誤判定がありました。

次が同時に表示される場合は、この誤判定です。

```text
[FAIL] The non-portable ch32fun NEWLIB include option is still present.
[PASS] Required exercise dry-runs contain no /usr/include/newlib path
```

`0.1.9-test10a`では、静的検査を`ch32fun.mk`の実際の
`-I$(NEWLIB)`オプションへ限定し、実効コマンドは必須演習3本の
`make -n build`で確認します。


## test12: `02_rotary_cursor_size`の`make list`が0台

まずUSB Device層を確認します。

```sh
ioreg -p IOUSB -l -w 0 > /tmp/uiap-rotary-usb.txt
grep -n -B 12 -A 24 -E 'UIAP Rotary Cursor macOS Test13|"idVendor" = 4617|"idProduct" = 49156' /tmp/uiap-rotary-usb.txt
```

判定:

- Productが旧`UIAP Rotary Cursor Test`、Serialが`TEST7-001`、または`bDeviceClass = 3`: test10a以前のファームウェア。test12で`make clean`から再書き込みする
- Productがtest12で`bDeviceClass = 0`だが`make list`が0台: `hidutil list`出力と`ioreg`全体を保存し、IOHIDの割り当てを調査する
- USB Device自体がない: ブートローダー書き込み成功とアプリケーション再列挙を分けて確認する

`make app-dry-run`へ進む条件は、`make list`が1台を表示することです。

## test11: `Cursor-scale API: PASS current=0.00`

`0.2.0-test11`で確認したネイティブホストの不具合です。

代表表示:

```text
Cursor-scale API: PASS current=0.00
[UIAP-CURSOR-E207] Could not set pointer scale 0.50.
[UIAP-CURSOR-E205] No saved pointer size is available.
```

判定:

- USB/IOHIDやエンコーダー入力の失敗ではない
- 非公開`CGSGetCursorScale`の返値を誤ったスカラー幅で解釈した可能性がある
- `0.00`は有効な倍率として保存・復元しない
- test11で`make app`を再実行しない

対応:

1. `0.2.2-test13`へ入れ替える
2. `setup`を再実行し、Devkit内Pythonとhidapiを復旧する
3. `make host-doctor`を実行する
4. `no-op-write=PASS`を確認する
5. その後に`make app`を実行する

期待例:

```text
Cursor-scale API: PASS abi=float32 current=1.00 no-op-write=PASS
```

test12は無効な旧状態ファイルを自動削除します。手動削除する場合はDevkit内の次だけを対象にします。

```sh
rm -f "$UIAP_DEVKIT_ROOT/.state/02_rotary_cursor_size.original-scale"
```


## test13: Python/hidapiホストが起動しない

```sh
doctor
versions
```

確認対象:

- `$UIAP_PYTHON`が`runtime/python/bin/python3`を指す
- Pythonがarm64
- `scripts/python/hidapi_probe.py`がPASS
- `host/cursor_size_host.py`をシステムPythonで直接実行していない

`build-host-tools`はtest13では使用しません。
