# macOS Apple Silicon検証範囲 — 0.2.2-test13

更新日: 2026-08-01

## 既存の確認済み基準

macOS 26.5.2、Apple Silicon arm64でtest12ネイティブCホストまで含め、必須演習3本の基本動作を確認済みです。演習02ではUSB/IOHID列挙、CW/CCW、サイズ変更、`Ctrl+C`復元が合格しました。

## test13で変更した境界

演習02のホスト実装をPythonへ置換しました。

- Devkit内Python 3.10.20
- hidapi 0.15.0 macOS arm64
- `host/cursor_size_host.py`
- private CoreGraphics/SkyLight APIはPython `ctypes`で動的参照
- `build-host-tools`なし

このため、test12のネイティブホスト実機結果はPython版test13の合格とは扱いません。

## test13で実機確認する項目

- `setup`でPython/hidapi取得・SHA-256検証・import
- `doctor`でPython arm64、hidapi、Pythonホスト構文、private API自己診断
- `make list`
- `make app-dry-run` CW/CCW
- `make host-doctor`
- `make app`サイズ変更
- `Ctrl+C`復元
- USB切断時復元
- `make restore`

非公開API、別Mac、別ユーザー、macOS 15最低対応、最終オフラインZIPは引き続き別途検証します。
