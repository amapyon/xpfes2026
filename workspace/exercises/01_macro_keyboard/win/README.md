# 01_macro_keyboard

センタースイッチ付きロータリーエンコーダーモジュールを1回押し込むと、USB HIDキーボードとして`AbCdE`を入力します。

## 検証状態

- 過去のWindows PoCとmacOS test10では同等機能を実機確認済み
- test17のWindows実機でコンパイルとリンクを確認済み（FLASH 2484 B、RAM 228 B）
- test17の書き込みコマンド不具合はtest19で修正済み
- 新モジュールでの書き込み、USB列挙、実入力を利用者実機で確認済み
- VID:PID `1209:C003`とシリアル`TEST3-001`はPoC用一時値

## 配線

| UIAPduino | モジュール |
|---|---|
| GND | GND |
| D8 / PC6 | S1 |
| D9 / PC7 | S2 |
| D5 / PC3 | KEY |
| 5V | 5V |

販売ページで指定されている動作電圧は5Vです。この演習で読み取る端子は`KEY`だけですが、次の演習と共通の5本を配線します。押し込み時はLowです。配線変更前にUSBを外してください。

## 実行

```text
cd /d "%UIAP_WORKSPACE%\exercises\01_macro_keyboard"
make clean
make
make size
make flash
```

書き込み後、メモ帳を開き、日本語IMEをOFFにしてエンコーダーの軸を1回押し込みます。コマンドプロンプト、PowerShell、パスワード欄では試さないでください。

列挙確認:

```text
make hidcheck
```

長押しでは繰り返しません。軸を離してから再度押し込むと、もう一度入力します。意図しない入力が続く場合はUSBケーブルを外してください。
