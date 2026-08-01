# macOS Apple Silicon実機検証計画 — 0.2.2-test13

## 1. 初期化

```sh
setup
build-minichlink
doctor
versions
```

成功条件: Python 3.10.20 arm64、hidapi import PASS、`FAIL=0`（既知リリースWARNを除く）。

## 2. 演習02

```sh
cd "$UIAP_WORKSPACE/exercises/02_rotary_cursor_size"
make clean
make
make size
make flash
make list
make host-doctor
make app-dry-run
```

`make list`期待値:

```text
Matching devices: 1
Product: UIAP Rotary Cursor macOS Test13
Serial: TEST13-002
```

`make host-doctor`期待例:

```text
Cursor-scale API: PASS abi=float32 current=1.00 no-op-write=PASS
```

`make app-dry-run`でCW/CCWを確認した後だけ次へ進みます。

```sh
make app
```

成功条件: サイズ変更、`Ctrl+C`終了時復元。続けてUSB切断時復元と`make restore`を別々に確認します。
