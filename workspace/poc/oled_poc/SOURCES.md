# 情報源と第三者コード

- `workspace/parts/PARTS_FOR_AI.md`: PART-09の確定事項・未確認事項
- `workspace/ai/BOARD_FOR_AI.md`: UIAPduinoのピン対応、電源、USB競合
- `workspace/poc/ws2812b8_hid_poc`: rv003usb Vendor-defined Feature Reportの構成
- Adafruit GFX `glcdfont.c`: 5×7 ASCIIビットマップの基礎
  - https://github.com/adafruit/Adafruit-GFX-Library/blob/master/glcdfont.c
  - BSD License、Copyright (c) 2012 Adafruit Industries
- Solomon Systech SSD1306 datasheet: 初期化コマンド、アドレッシング、表示RAM構成
  - 実際のPART-09モジュールの電気仕様を補完する根拠には使用しない

`oled_poc.c`にはAdafruit GFXのASCII `0x20`～`0x7E`に対応する部分を保持し、
縦7ピクセル要件に合わせて描画時にbit 7をマスクしています。
