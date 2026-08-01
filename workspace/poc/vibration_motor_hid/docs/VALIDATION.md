# 検証状態

## Windows 11 x64

既存PoC `WIN-HID-MOTOR-001` と、構成変更後の再検証 `WIN-HID-MOTOR-002` で以下を実機確認済みです。

- UIAPduino Pro Micro CH32V003 V1.4
- ブートローダー `1209:B803`
- Vendor-defined USB HID Feature Report
- アプリケーション `1209:D003`
- 振動レベル `1`～`100`
- 数値に応じた振動強度の変化
- `status`
- `off`
- `make on 99` と `make on 100` に体感できる差なし

### 2026-08-01 構成変更後の再検証

利用者のWindows 11 x64実機で、`FUNCONF_SYSTICK_USE_HCLK 1`を追加した構成変更後のファームウェアを確認しました。

- Devkit同梱`riscv-none-elf-gcc`によるクリーンビルド成功
- `make flash`による書き込み成功
- アプリケーションUSB HIDとしての動作確認
- PC側からの振動モーター制御と物理動作を確認

検証IDは`WIN-HID-MOTOR-002`です。実機動作は利用者報告、ビルド結果は同一ソースを使ったローカル再現結果です。

## macOS Apple Silicon

この振動モーターHID PoC自体の実機検証は未実施です。

DevkitとしてPython/hidapiを使える構成は存在しますが、このPoCの
ビルド、書き込み、Feature Report、モーター動作を別途確認してください。

## 今回追加したもの

- `host/motorctl.py`
- `make play`
- 既定パターン `100:0.1,0:0.4`
- 共通ソースの`src/`への移動
- Devkit同梱Python、hidapi、ツールチェーンを使う共通Makefile
- `make host`、`make doctor`、`make list`、`make size`、`make check-deps`
- macOS接続時のHID `GET_IDLE` / `SET_IDLE`応答

`make play`は既存のレベル制御プロトコルをホストから周期的に送る追加機能です。
ホストのパターン解析自己テストとPython構文検査は通過しています。

構成変更後のWindows版ファームウェアは、Devkit同梱の`riscv-none-elf-gcc`でクリーンビルド済みです。Flash使用量は2,920 bytes（17.82%）、RAM使用量は216 bytes（10.55%）でした。

構成変更後のWindows版について、書き込み、USB HID制御、モーター動作を実機確認済みです。macOS版のビルド、書き込み、列挙、HID送受信、モーター動作は未検証です。
