# 01_macro_keyboard

センタースイッチ付きロータリーエンコーダーモジュールの押し込み操作で`AbCdE`を入力するUSB HIDキーボード演習です。ファームウェア、USB設定、列挙確認スクリプトはWindowsとmacOSで共通です。

[指定のモジュール](https://electronicwork.shop/items/64b9e54b9dd503007bc60458)は`GND / S1 / S2 / KEY / 5V`表記の5ピン品です。この演習では`KEY`を読み、同じ配線のまま`02_rotary_cursor_size`では`S1`と`S2`を使用します。

## 検証状態

- 新モジュールを使用した従来のOS別実装は、WindowsとmacOSの両方で実機確認済み
- 共通化後の単一ファームウェアを、WindowsとmacOSの両方で利用者実機確認済み
- VID:PID `1209:C003`とシリアル`TEST3-001`はPoC用一時値

## 配線

| UIAPduino | モジュール |
|---|---|
| GND | GND |
| D8 / PC6 | S1 |
| D9 / PC7 | S2 |
| D5 / PC3 | KEY |
| 5V | 5V |

販売ページで指定されている動作電圧は5Vです。この演習で読み取る端子は`KEY`だけですが、次の演習と共通の5本を配線します。押し込み時はLowです。配線変更前にUSBを外してください。

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

macOSで初回キーボード設定アシスタントが表示された場合は、存在しない識別キーを押さず、前の画面へ戻って「終了」で閉じます。
