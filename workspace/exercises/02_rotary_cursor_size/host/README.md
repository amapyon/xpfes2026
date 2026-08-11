# Cross-platform host application

`cursor_size_host.py`は、Windows 11とmacOS Apple Siliconで共用する`02_rotary_cursor_size`のホストアプリケーションです。

共通部分:

- `1209:C004`のHID列挙、1台接続確認、`open_path`
- Report IDなしの`[delta, sequence]`入力デコード
- CW／CCWイベントループとドライラン
- コマンドライン、`Ctrl+C`、終了時復元の制御

OS固有部分:

- Windows: レジストリと`SystemParametersInfoW(0x2029)`
- macOS: 非公開`CGSGetCursorScale` / `CGSSetCursorScale`とABI判定

参加者はPythonファイルを直接実行せず、演習ルートで次を使用します。

```text
make host-doctor
make hidcheck
make app-dry-run
make cursor-test
make app
make restore
```

状態ファイルは既存形式を維持します。

- Windows: `.state/cursor-size-before.json`
- macOS: `.state/02_rotary_cursor_size.original-scale`
