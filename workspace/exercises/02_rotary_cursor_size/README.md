# 02_rotary_cursor_size

[指定のセンタースイッチ付きロータリーエンコーダーモジュール](https://electronicwork.shop/items/64b9e54b9dd503007bc60458)の回転入力でOSのポインターサイズを変更する演習です。`01_macro_keyboard`と同じ5本の配線を使用します。ホスト側処理はOS APIが異なるため、`win/`と`mac/`に分けています。

このモジュールを使用した想定動作をWindows、macOSの両方で実機確認済みです。

```console
make
make flash
make app-dry-run
make app
make restore
```

ホストアプリは終了時に起動前の設定を復元します。実機確認状況は各プラットフォーム側のREADMEを参照してください。

## Macで書き込んだファームウェアをWindowsで使う場合

Mac test13ファームウェアは、HID入力を`[delta, sequence]`の2バイトで送信します。Report IDは使用していません。Windowsホストは必ず先頭バイトを移動量として読み、2バイト目の診断用連番を無視します。

Windowsの`make app-dry-run`で、静止中は何も表示されず、エンコーダーを回した時だけCW／CCWが表示されることを実機確認済みです。
