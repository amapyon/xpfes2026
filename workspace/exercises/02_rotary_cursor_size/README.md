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
