# Host applications

回転入力ファームウェアとHIDレポートはWindows/macOS共通です。ポインターサイズを変更するOS APIだけが異なるため、ホストアプリケーションを次に分けています。

- `win/cursor_size_host.py`: Windows 11用
- `mac/cursor_size_host.py`: macOS Apple Silicon用

参加者はPythonファイルを直接実行せず、演習ルートの`make app`などを使用します。
