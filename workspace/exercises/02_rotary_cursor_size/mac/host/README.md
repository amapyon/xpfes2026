# macOS Python cursor host — test13

`cursor_size_host.py`は、Devkit内Pythonと`hidapi`で`1209:C004`の入力レポートを受信するmacOS Apple Silicon向けホストアプリです。

- Product: `UIAP Rotary Cursor macOS Test13`
- Serial: `TEST13-002`
- Python: Devkit内Python 3.10.20（test13オンライン検証版）
- USB: `hidapi` 0.15.0
- カーソルAPI: Python `ctypes`から非公開`CGSGetCursorScale` / `CGSSetCursorScale`を参照

Windows版と同じくホストアプリをPythonへ統一する方針です。参加者はPythonファイルを直接実行せず、演習ディレクトリで`make list`、`make host-doctor`、`make app-dry-run`、`make app`、`make restore`を使用します。

## 安全対策

- `float32` / `float64` ABIを実行時判定
- `host-doctor`で現在値の同値書込みと再読取りを確認
- `0.00`、NaN、範囲外値を状態ファイルへ保存しない
- 各変更後と復元後に再読取りして確認
- `Ctrl+C`およびHID読取り例外時に保存値の復元を試みる

非公開APIを使用するため、test12のネイティブC実装の成功をPython版test13へ流用せず、実機で再検証します。
