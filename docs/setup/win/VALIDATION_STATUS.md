# 検証状態

対象: `0.6.2-test19`

## Windows実機で確認済み

- オンライン`setup`完走
- `doctor`主要検査
- `01_macro_keyboard`: ビルド、書き込み、HIDキーボード入力
- `02_rotary_cursor_size`: ビルド、書き込み、`1209:C004`列挙
- `02_rotary_cursor_size`: `make app-dry-run`でCW／CCW受信

## test18で確認した不具合

`make app`は起動前サイズ80を読み取り、対象HIDを1台開いた後、最初のサイズ反映で次のエラーになりました。

```text
[WinError 6] ハンドルが無効です。
```

原因は、ポインターサイズ変更後の再読込に`SPI_SETCURSORS (0x0057)`を使用したことです。プロジェクトの過去のPoCでも同じエラーが確認され、v1.0.7で`0x2029`へ変更して解消していました。

## test19で修正・静的確認済み

- `SPI_SETCURSORS (0x0057)`を削除
- 過去のWindows実機PoCで確認した`SystemParametersInfoW`アクション`0x2029`へ変更
- `CursorBaseSize`と`Software\Microsoft\Accessibility\CursorSize`を保存・復元
- test17/test18形式の保存状態を移行可能
- 前回異常終了の保存状態を`make app`起動前に自動復元
- `make cursor-test`を追加
- Python構文、自己診断、ZIP、manifest、BOM、改行を静的検査

## 再確認待ち

- `make restore`によるtest18残存状態の復元
- `make cursor-test`のサイズ変更と復元
- `make app`のCW／CCWサイズ変更
- `Ctrl+C`終了時の起動前サイズ復元
- USB切断時の保存状態保持と、その後の`make restore`
- 別Windows 11 PC、別ユーザー
- 最終オフラインZIP
