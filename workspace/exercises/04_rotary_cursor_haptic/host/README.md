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

共通ホストはポインターサイズを変更して再読取りに成功した後、Report ID 2のFeature Reportを送り、ファームウェアに約60msの振動を要求します。上限／下限、ドライラン、変更失敗時には送りません。

参加者はPythonファイルを直接実行せず、演習ルートの`make app`などを使用します。
