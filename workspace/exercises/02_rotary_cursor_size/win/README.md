# 02_rotary_cursor_size

3端子ロータリーエンコーダーのCW／CCWをVendor-defined HIDでPCへ送り、Windowsのマウスポインターサイズを16単位ずつ変更します。

## 検証状態

- Windows test18でビルド、書き込み、USB HID列挙、`make app-dry-run`のCW／CCW受信を確認済み
- test18の`make app`は`SPI_SETCURSORS (0x0057)`により`WinError 6`で停止
- test19は、過去の検証済みWindows PoCと同じ`0x2029`即時反映方式へ修正
- test19の`make cursor-test`、`make app`、`Ctrl+C`復元は再確認待ち
- VID:PID `1209:C004`、製品名`UIAP RE12000 Cursor Test`、シリアル`TEST7-001`はPoC用一時値

## 配線

| UIAPduino | エンコーダー |
|---|---|
| D8 / PC6 | A |
| GND | C |
| D9 / PC7 | B |

内部プルアップを使用します。C端子を3.3Vまたは5Vへ接続しないでください。配線変更前にUSBを外してください。

## ビルドと書き込み

```text
cd /d "%UIAP_WORKSPACE%\exercises\02_rotary_cursor_size"
make clean
make
make size
make flash
```

## 段階確認

```text
make doctor
make hidcheck
make app-dry-run
make cursor-test
```

`make cursor-test`は現在のサイズから16単位だけ変更し、約0.8秒後に元へ戻します。HID入力とWindows設定変更を分けて確認できます。

## 実行

```text
make app
```

終了は`Ctrl+C`です。正常終了時に起動前のサイズへ戻します。前回異常終了の保存状態がある場合、test19は起動前に自動復元します。

手動復元:

```text
make restore
```

回転方向が想定と逆の場合は、USBを外してAとBを入れ替えます。
