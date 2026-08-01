# 02_rotary_cursor_size

[指定のセンタースイッチ付きロータリーエンコーダーモジュール](https://electronicwork.shop/items/64b9e54b9dd503007bc60458)の回転入力でOSのポインターサイズを変更する演習です。ファームウェアとUSB設定はWindows/macOS共通で、OS APIが異なるホスト処理だけを`host/win`と`host/mac`に分けています。

## 検証状態

- 従来のOS別実装はWindows、macOSとも想定動作を実機確認済み
- 共通化後の単一ファームウェアは両OSで再確認が必要
- VID:PID `1209:C004`とシリアル`TEST7-001`はPoC用一時値

## 配線

| UIAPduino | モジュール |
|---|---|
| GND | GND |
| D8 / PC6 | S1 |
| D9 / PC7 | S2 |
| D5 / PC3 | KEY |
| 5V | 5V |

販売ページで指定されている動作電圧は5Vです。この演習では`S1`と`S2`を読み、`KEY`は配線したまま使用しません。配線変更前にUSBを外してください。

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

`make app-dry-run`はポインターサイズを変更せずCW／CCWだけを表示します。`make app`は回転に合わせてサイズを変更し、`Ctrl+C`終了時に起動前の値へ戻します。

異常終了後の手動復元:

```text
make restore
```

共通HIDレポートは`[delta, sequence]`の2バイトです。Report IDは使用しません。両OSのホストは先頭バイトを移動量として読み、2バイト目の診断用連番を無視します。

回転方向が想定と逆の場合は、USBを外して`S1`と`S2`を入れ替えます。
