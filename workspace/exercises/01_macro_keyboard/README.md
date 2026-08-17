# 01_macro_keyboard

センタースイッチ付きロータリーエンコーダーモジュールの押し込み操作で`AbCdE`を入力するUSB HIDキーボード演習です。ファームウェア、USB設定、列挙確認スクリプトはWindowsとmacOSで共通です。

[指定のモジュール](https://electronicwork.shop/items/64b9e54b9dd503007bc60458)は`GND / S1 / S2 / KEY / 5V`表記の5ピン品です。この演習では`GND`と`KEY`の2本だけを接続します。次の`02_rotary_cursor_size`で`S1`、`S2`、`5V`の3本を追加します。

## 検証状態

- 新モジュールを使用した従来のOS別実装は、WindowsとmacOSの両方で実機確認済み
- 共通化後の単一ファームウェアを、WindowsとmacOSの両方で利用者実機確認済み
- `GND`と`KEY`だけの2本配線で、従来と同じ`AbCdE`入力を利用者実機確認済み
- VID:PIDは共有テスト用`1209:0001`、Product文字列は`UIAP Macro Keyboard`
- `1209:0001`は世界で一意ではなく、教育目的の試作とワークショップ内テスト専用。製品、製造、販売、再配布には使用しない

## 配線

| UIAPduino | モジュール |
|---|---|
| GND | GND |
| D5 / PC3 | KEY |

PC3の内部プルアップを使用するため、この演習ではモジュールの`5V`接続は不要です。押し込み時は`KEY`と`GND`が導通してLowになります。`S1`、`S2`、`5V`は接続しません。配線変更前にUSBを外してください。

## ビルドと書き込み

Windows:

```text
cd /d "%UIAP_WORKSPACE%\exercises\01_macro_keyboard"
make clean
make
make size
make flash
```

macOS:

```sh
cd "$UIAP_WORKSPACE/exercises/01_macro_keyboard"
make clean
make
make size
make flash
```

## 入力確認

メモ帳やテキストエディットなど安全な入力欄を開き、日本語IMEをOFFにしてエンコーダーの軸を1回押し込みます。

- 1回押すと`AbCdE`
- 押し続けても繰り返さない
- 軸を離して再度押すと再送する
- キーが押されたままにならない

コマンド入力欄、パスワード欄、ブラウザのアドレス欄では試さないでください。意図しない入力が続く場合はUSBケーブルを外してください。

列挙確認:

```text
make hidcheck
```

成功時は次の形式で表示されます。`Product:`が`UIAP Macro Keyboard`であり、最終行にも同じ名称が表示されることを確認してください。

```text
Matching devices: 1
[0] VID:PID=1209:0001
  Product: UIAP Macro Keyboard
  Serial: TEST3-001
UIAP Macro Keyboard HID enumeration: PASS
```

Product名が異なる場合は次へ進まず、この演習のファームウェアを書き込んだか確認します。

macOSで初回キーボード設定アシスタントが表示された場合は、存在しない識別キーを押さず、前の画面へ戻って「終了」で閉じます。
