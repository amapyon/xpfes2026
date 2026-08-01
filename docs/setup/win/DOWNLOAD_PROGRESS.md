# ダウンロード進捗と復旧

## 実装

- 実行ファイル: `%SystemRoot%\System32\curl.exe`
- リダイレクト: `--location`
- HTTPエラー: `--fail`
- 再試行: `--retry 3 --retry-delay 2`
- 接続タイムアウト: `--connect-timeout 30`
- 進捗: `--progress-bar`
- 再開: `.part`がある場合に`--continue-at -`
- 完了判定: SHA-256一致後に正式ファイル名へ変更

## ファイル

```text
runtime\downloads\<archive>.part
runtime\downloads\<archive>
runtime\downloads\<archive>.bad-YYYYMMDD-HHMMSS
```

`.part`は未完了、`.bad-*`はSHA-256不一致として隔離したファイルです。

## 代表的なcurl終了コード

- 6: ホスト名を解決できない
- 7: 接続できない
- 28: タイムアウト
- 33: Range再開に非対応。このDevkitは先頭から自動再取得する
- 35: TLS接続失敗
- 60: 証明書検証失敗
