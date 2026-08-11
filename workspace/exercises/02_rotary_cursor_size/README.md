# 02_rotary_cursor_size

[指定のセンタースイッチ付きロータリーエンコーダーモジュール](https://electronicwork.shop/items/64b9e54b9dd503007bc60458)の回転入力でOSのポインターサイズを変更する演習です。ファームウェア、USB設定、ホストアプリはWindows/macOS共通です。単一の`host/cursor_size_host.py`が実行時にOSを判定し、Windowsではレジストリと`SystemParametersInfoW`、macOSではCoreGraphics/SkyLightの非公開APIを使用します。

## 検証状態

- 統合後の共通ホストと単一ファームウェアはWindows/macOSで想定動作を実機確認済み
- macOSではDevkit `v0.1.2`の演習手順を利用者実機で合格確認済み
- VID:PID `1209:C004`とシリアル`TEST7-001`はPoC用一時値

## 配線

`01_macro_keyboard`で接続した`GND`と`KEY`を残し、USBを外してから`S1`、`S2`、`5V`の3本を追加します。

| UIAPduino | モジュール | この演習での扱い |
|---|---|---|
| GND | GND | `01`から継続 |
| D5 / PC3 | KEY | `01`から継続。`02`では未使用 |
| D9 / PC7 | S1 | 追加 |
| D8 / PC6 | S2 | 追加 |
| 5V | 5V | 追加。赤い配線 |

販売ページで指定されている動作電圧は5Vです。この演習では`S1`と`S2`を読み、`KEY`は配線したまま使用しません。5V接続時は、UIAPduinoのマイクロコントローラー電源が初期状態の5V設定であることを前提とします。

## ビルドと書き込み

```text
make clean
make
make size
make flash
```

## 段階確認と実行

```text
make host-doctor
make hidcheck
make app-dry-run
make cursor-test
make app
```

`make hidcheck`では次の形式で表示されます。`Product:`が`UIAP Rotary Cursor`であり、最終行にも同じ名称が表示されることを確認してください。

```text
Matching devices: 1
[0] VID:PID=1209:C004
  Product: UIAP Rotary Cursor
  Serial: TEST7-001
UIAP Rotary Cursor HID enumeration: PASS
```

Product名が異なる場合は次へ進まず、この演習のファームウェアを書き込んだか確認します。

`make app-dry-run`はポインターサイズを変更せずCW／CCWだけを表示します。`make app`は回転に合わせてサイズを変更し、`Ctrl+C`終了時に起動前の値へ戻します。

異常終了後の手動復元:

```text
make restore
```

共通HIDレポートは`[delta, sequence]`の2バイトです。Report IDは使用しません。両OSのホストは先頭バイトを移動量として読み、2バイト目の診断用連番を無視します。

回転方向が想定と逆の場合は、USBを外して`S1`と`S2`を入れ替えます。
