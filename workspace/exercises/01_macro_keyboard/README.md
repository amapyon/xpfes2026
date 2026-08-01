# 01_macro_keyboard

センタースイッチ付きロータリーエンコーダーモジュールの押し込み操作で`AbCdE`を入力するUSB HIDキーボード演習です。現在はWindows test19とMac test13の実機確認済み実装を分けて保持しています。

[指定のモジュール](https://electronicwork.shop/items/64b9e54b9dd503007bc60458)は`GND / S1 / S2 / KEY / 5V`表記の5ピン品です。この演習では`KEY`を読み、同じ配線のまま`02_rotary_cursor_size`では`S1`と`S2`を使用します。

このモジュールを使用した想定動作をWindows、macOSの両方で実機確認済みです。

```console
make
make flash
make app
```

`make app`は接続したHIDキーボードを列挙して確認します。
