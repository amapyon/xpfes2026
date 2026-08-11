# 振動モーター操作ホスト

`motorctl.py`は、Windows 11とmacOS Apple Siliconで共用するホストプログラムです。Vendor-defined HID Feature Reportを使用して振動レベルを`0`〜`100`で制御します。

通常は直接Pythonを実行せず、演習フォルダーで次のMakeターゲットを使用します。

```text
make host-doctor
make list
make pulse
make pulse LEVEL=75
make on LEVEL=75
make status
make off
```

`make on`の後は必ず`make off`を実行してください。短時間の確認には、自動的にOFFへ戻る`make pulse`を推奨します。
