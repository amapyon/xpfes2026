# 振動モーター操作ホスト

`motorctl.py`は、Windows 11とmacOS Apple Siliconで共用するホストプログラムです。Vendor-defined HID Feature Reportを使用し、LEVEL、ON時間、OFF時間、回数を一括送信します。パターンの実行と自動停止はデバイス側が行います。

通常は直接Pythonを実行せず、演習フォルダーで次のMakeターゲットを使用します。

```text
make host-doctor
make hidcheck
make list
make pulse
make pulse LEVEL=75
make pattern LEVEL=95 ON_MS=80 OFF_MS=40 COUNT=2
make on LEVEL=75
make status
make off
```

`make on`の後は必ず`make off`を実行してください。短時間の確認には、デバイスが自動的にOFFへ戻る`make pulse`または`make pattern`を推奨します。
