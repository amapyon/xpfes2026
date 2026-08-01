# 02_rotary_cursor_size

ロータリーエンコーダのHID入力でOSのポインターサイズを変更する演習です。ホスト側処理はOS APIが異なるため、`win/`と`mac/`に分けています。

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
