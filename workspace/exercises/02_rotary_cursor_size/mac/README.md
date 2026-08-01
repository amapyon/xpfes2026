# 02_rotary_cursor_size

D8 / D9へ接続した3端子ロータリーエンコーダーの回転をVendor-defined HIDでMacへ送り、PythonホストアプリでmacOSのポインターサイズを変更します。

## test13の変更

macOS版ホストアプリをネイティブC CLIからPythonへ変更しました。

```text
host/cursor_size_host.py
```

- Devkit内Pythonを使用し、システムPythonを使用しない
- HID受信は`hidapi`を使用
- カーソルサイズ変更はPython `ctypes`からtest12で検証した非公開CoreGraphics/SkyLight APIを呼び出す
- test12で有効だった`float32` / `float64` ABI判定、同値書込み、再読取り、状態保存・復元をPythonへ移植
- Product: `UIAP Rotary Cursor macOS Test13`
- Serial: `TEST13-002`

test12ネイティブ版の実機合格は履歴として保持しますが、Python版test13のHID受信・サイズ変更・復元は別途実機再検証します。

## 配線

| UIAPduino | エンコーダー |
|---|---|
| D8 / PC6 | A |
| GND | C（共通端子） |
| D9 / PC7 | B |

3.3Vまたは5Vへ接続しません。固定用金属タブを信号端子と混同しないでください。配線前にUSBを外します。

## ファームウェア

```sh
make clean
make
make size
make flash
```

## USB/HID列挙

```sh
make list
```

期待値:

```text
Matching devices: 1
Product: UIAP Rotary Cursor macOS Test13
Serial: TEST13-002
```

## Pythonホスト自己診断

```sh
make host-doctor
```

期待例:

```text
Cursor-scale API: PASS abi=float32 current=1.00 no-op-write=PASS
```

`abi`は`float32`または`float64`です。`current=0.00`は合格にしません。

## HID入力のみ確認

```sh
make app-dry-run
```

ポインターサイズを変更せず、CWまたはCCWを表示します。

## 実動作

`host-doctor`と`app-dry-run`が成功した後に実行します。

```sh
make app
```

- CW: 0.25段階大きくする
- CCW: 0.25段階小さくする
- 操作範囲: 0.50～4.00
- 終了: `Ctrl+C`
- 正常終了時: 起動前サイズへ復元し、再読取りで一致確認

異常終了後:

```sh
make restore
```

## 実装上の注意

Python化してもカーソルサイズ変更部分はAppleの公開SDKとして保証されていないAPIに依存します。Python化の目的はWindows/macOSでホストアプリの言語と配布方式を揃えることであり、非公開APIの将来互換性を改善するものではありません。

アプリケーションVID:PID `1209:C004`とUSBシリアル`TEST13-002`はPoC用一時値です。
