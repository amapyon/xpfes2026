# Cross-platform host application

`cursor_size_host.py`は、Windows 11とmacOS Apple Siliconで共用する`04_rotary_cursor_haptic`のホストアプリケーションです。

共通部分:

- `1209:C005`のHID列挙、1台接続確認、`open_path`
- Report ID 1の`[delta, sequence]`入力デコード
- Feature Report ID 2による触覚指示
- CW／CCWイベントループ、ドライラン、終了時復元

OS固有部分:

- Windows: レジストリと`SystemParametersInfoW(0x2029)`
- macOS: 非公開`CGSGetCursorScale` / `CGSSetCursorScale`とABI判定

共通ホストは回転中にはポインターサイズだけを変更し、最後の回転から200ms後にReport ID 2のFeature Reportを送ります。03と同じ形式でLEVEL、ON時間、OFF時間、回数を一括送信し、パターン実行と自動停止はデバイス側へ任せます。通常変更は`95, 80ms, 40ms, 2回`、上限／下限は`95, 250ms, 0ms, 1回`です。連続回転中は最後の結果と時刻で保留中の指示を更新します。ドライランと変更失敗時には送りません。

参加者はPythonファイルを直接実行せず、演習ルートの`make hidcheck`、`make app`などを使用します。`make hidcheck`はProduct名`UIAP Rotary Haptic`の完全一致を確認します。
