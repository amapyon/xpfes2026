# Windows 11 x64 セットアップ

対象: UIAP Devkit `0.6.2-test19`

1. ZIPを新しい空フォルダーへ完全に展開する。
2. `start-uiap.cmd`をダブルクリックする。
3. 次を順に実行する。

```text
setup
doctor
versions
```

`setup`はBuild Tools、RISC-V GCC、Python、hidapi、ch32funをSHA-256検証後に配置します。rv003usbは固定コミットURLから必要ソースを取得し、実測SHA-256を`workspace\deps\rv003usb\SOURCE_FILES.sha256`へ記録します。

`doctor`がFAILの場合は演習へ進まず、`report`の出力を保存してください。

`doctor`がPASSしたら、演習へ進む前にUIAPduinoのUSB HID事前診断を実行します。

```text
cd /d "%UIAP_WORKSPACE%\preflight"
make
make flash
make preflight
```

最後に`RESULT: PASS`と表示されることを確認します。詳細と失敗時の対処は`workspace\preflight\README.md`を参照してください。
