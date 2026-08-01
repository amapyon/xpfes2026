# 01_macro_keyboard

D5 / PC3とGNDの間に接続したモメンタリスイッチを1回押すと、USB HIDキーボードとして`AbCdE`を入力します。

## 検証状態

- 過去のWindows PoCとmacOS test10では同等機能を実機確認済み
- test17のWindows実機でコンパイルとリンクを確認済み（FLASH 2484 B、RAM 228 B）
- test17の書き込みコマンド不具合はtest19で修正済み
- test19での書き込み、USB列挙、実入力は再確認待ち
- VID:PID `1209:C003`とシリアル`TEST3-001`はPoC用一時値

## 配線

| UIAPduino | スイッチ |
|---|---|
| D5 / PC3 | 一方の端子 |
| GND | もう一方の端子 |

内部プルアップを使用します。配線変更前にUSBを外してください。

## 実行

```text
cd /d "%UIAP_WORKSPACE%\exercises\01_macro_keyboard"
make clean
make
make size
make flash
```

書き込み後、メモ帳を開き、日本語IMEをOFFにしてスイッチを1回押します。コマンドプロンプト、PowerShell、パスワード欄では試さないでください。

列挙確認:

```text
make hidcheck
```

長押しでは繰り返しません。スイッチを離してから再度押すと、もう一度入力します。意図しない入力が続く場合はUSBケーブルを外してください。
