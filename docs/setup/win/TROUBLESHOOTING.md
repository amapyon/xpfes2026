# トラブルシューティング

## `setup`が`UIAP-E133`で停止する

`VERSION`と`config\win\bootstrap.lock.json`のDevkit版が異なる配布物です。`0.1.0`のWindows版には`VERSION=0.1.0`と`lock=0.1.0-dev`の不整合があり、セットアップは依存ファイルを取得する前に停止します。

展開済みファイルを直接書き換えず、`0.1.1`以降の修正版ZIPを新しい空フォルダーへ展開してください。再実行後も停止する場合は、`logs\win\setup-*.log`と`VERSION`を管理者へ共有してください。

## `make app`で`[WinError 6] ハンドルが無効です`

`0.6.1-test18`の既知不具合です。HID受信ではなく、Windowsポインターサイズ反映処理で失敗しています。

次の条件ならHID側は正常です。

- `make hidcheck`がPASS
- `make app-dry-run`でCW／CCWが表示される
- `make app`が`Original pointer size`と`Mode: apply`を表示した後にWinError 6で停止する

原因は`SPI_SETCURSORS (0x0057)`の使用です。test19は過去の検証済みPoCと同じ`0x2029`方式へ修正しています。

### test19適用後

前回の保存状態を先に復元します。

```text
cd /d "%UIAP_WORKSPACE%\exercises\02_rotary_cursor_size"
make restore
make cursor-test
make app
```

`make restore`が「Saved cursor state was not found」と表示する場合、保存状態がないため`make cursor-test`へ進めます。

## ポインターサイズが戻らない

```text
cd /d "%UIAP_WORKSPACE%\exercises\02_rotary_cursor_size"
make restore
```

保存状態ファイル:

```text
%UIAP_DEVKIT_ROOT%\.state\cursor-size-before.json
```

手動で削除せず、まず`make restore`を実行してください。

## `make app-dry-run`は成功するが`make app`が失敗する

- `app-dry-run`成功: USB列挙、hidapi、レポート受信、エンコーダー配線は正常
- `app`失敗: Windows設定変更または復元処理を確認

HIDと設定変更を分離するには次を使用します。

```text
make cursor-test
```

## `make flash`でminichlinkのUsageが表示される

`0.6.0-test17`の既知不具合です。test18以降を使用してください。
