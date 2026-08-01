# Windows Python cursor host

共有エンコーダーHIDファームウェアから`[delta, sequence]`レポートを受信し、Windowsのポインターサイズを変更します。先頭バイトだけを移動量として読み、2バイト目の診断用連番は無視します。

演習ルートの`make host-doctor`、`make app-dry-run`、`make cursor-test`、`make app`、`make restore`から実行します。
