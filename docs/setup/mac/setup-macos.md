# macOS Apple Siliconセットアップ — test13

対象: macOS Sequoia 15以降、Apple Silicon arm64

このパッケージは主催者実機検証用のオンライン初期化版です。参加者向け最終版ではありません。

## 主催者用オンライン初期化

```sh
setup
build-minichlink
doctor
versions
```

`setup`はGNU Make、RISC-V GCC、Python 3.10.20、hidapi 0.15.0、固定コミットの依存ソースを取得します。演習02のPythonホストはコンパイル不要なので`build-host-tools`は廃止しました。

参加者向け最終版では、Pythonとhidapiを完成済みランタイムとして同梱し、当日のネットワーク接続や`pip install`を要求しません。

## 検証順

```sh
cd "$UIAP_WORKSPACE/preflight"
make clean
make flash
make preflight

cd "$UIAP_WORKSPACE/exercises/00_onboard_led_blink"
make clean
make flash

cd "$UIAP_WORKSPACE/exercises/01_macro_keyboard"
make clean
make flash

cd "$UIAP_WORKSPACE/exercises/02_rotary_cursor_size"
make clean
make flash
make list
make host-doctor
make app-dry-run
make app
```

`workspace/preflight`の事前診断は、2026-08-05にmacOS実機で動作確認済みです。
