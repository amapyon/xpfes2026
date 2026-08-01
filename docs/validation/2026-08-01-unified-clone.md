# 統合リポジトリの実機確認（2026-08-01）

## 確認済み

- macOS: `00_onboard_led_blink`、`01_macro_keyboard`、`02_rotary_cursor_size`
- Windows: `00_onboard_led_blink`、`01_macro_keyboard`
- Macで書き込んだ`02_rotary_cursor_size`ファームウェアをWindowsホストから列挙
- Windows: Mac test13ファームウェアを接続した`02_rotary_cursor_size`の`make app-dry-run`
- Windows: エンコーダー静止中は値が表示されず、回転操作時だけ期待するCW／CCWが表示される

## Windows 02で見つかった互換性不具合

Mac test13ファームウェアの入力レポートは`[delta, sequence]`の2バイトである。HID Report DescriptorはReport IDを宣言していない。

Windowsホストは、先頭の`delta`が0のときに、その0をReport IDと誤認して2バイト目の`sequence`を相対移動量として読んでいた。このため、エンコーダー静止中にも`-35, -34, -33, ...`のような連続値が表示された。

修正後は常に先頭バイトを`delta`として読み、2バイト目は無視する。自己診断には、静止レポート`[0, sequence]`が0になる回帰ケースを含める。

## 修正後の実機結果

Mac test13ファームウェアを書き込んだデバイスをWindowsへ接続し、修正後の`make app-dry-run`が想定どおり動作することを利用者が確認した。

## 再確認待ち

- `make app`終了時にWindowsのポインターサイズが復元されること
