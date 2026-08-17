# UIAPduinoの情報（生成AI向け）

このファイルは、自由制作`device1`の要件整理、配線設計、ch32funによるプログラム作成に使用する正本です。対象は`UIAPduino Pro Micro CH32V003 V1.4`と、このDevkitに収録された開発環境です。

## 絶対条件

- マイコンは`CH32V003F4U6`、動作周波数は48MHz
- プログラムはArduinoスケッチではなく、Devkit収録の`ch32fun`を使うC言語で作成する
- GPIOは`PC3`のようなch32funの端子名で記述する。`5`のようなArduino端子番号をch32funへ流用しない
- 部品の端子、電圧、電流、信号形式が未確認の場合は推測で接続しない
- 配線変更前にUSBケーブルを外す
- `WIRING.md`の安全確認が完了するまで、書き込みと実機接続を指示しない

## 電源

- マイコン電源は基板のジャンパーで3.3Vまたは5Vを選択でき、出荷時設定は5V
- ワークショップでは、主催者から別の指示がない限り出荷時の5V設定を前提とする
- 基板の`3.3V`端子と`5V`端子は、マイコン電源設定を切り替えても同じ名前の電圧出力として扱う。電源端子はPro Micro互換ボードと完全互換ではない
- 5V動作の部品であっても、信号端子がマイコンGPIOへ直接接続可能とは限らない。各部品の信号条件を確認する
- GPIOからモーター、LED、ブザーなどへ供給できる電流を推測しない。ドライバー、抵抗、レベル変換などの要否を部品ごとに確認する
- USB給電の保護回路があっても、誤配線や接続部品の破損を防止できるとは限らない

## 端子対応

次の対応はUIAP公式のArduino variantに基づきます。ch32funのプログラムでは右列の端子名を使用します。

| 基板表記 | ch32fun端子 | 主な確認済み用途・注意 |
|---|---|---|
| D0 / A1 | PA1 | ADC A1として使用可能 |
| D1 / A0 | PA2 | ADC A0として使用可能 |
| D2 | PC0 | 基板上LED。Highで点灯、Lowで消灯 |
| D3 | PC1 | I2C SDA候補 |
| D4 | PC2 | I2C SCL候補 |
| D5 | PC3 | 演習でスイッチ入力、内部プルアップを確認済み |
| D6 / A2 | PC4 | ADC A2、TIM1_CH4。演習で振動モジュールINを制御 |
| D7 | PC5 | SPI1 SCK候補 |
| D8 | PC6 | SPI1 MOSI。演習でエンコーダー入力、PoCでWS2812B出力に使用 |
| D9 | PC7 | SPI1 MISO候補。演習でエンコーダー入力に使用 |
| D10 | PD0 | 用途を決める前に周辺機能競合を確認する |
| D11 | PD1 | SWIO。使用するとデバッグ／書き込み経路へ影響するため自由制作では原則使用しない |
| D12 / A3 | PD2 | ADC A3として使用可能 |
| D13 / A4 | PD3 | ADC A4。rv003usb使用時はUSB D+ |
| D14 / A7 | PD4 | ADC A7。rv003usb使用時はUSB D- |
| D15 / A5 | PD5 | ADC A5。UART TX候補。rv003usb使用時はプルアップ制御 |
| D16 / A6 | PD6 | ADC A6。UART RX候補 |
| D17 | PD7 | 用途を決める前に周辺機能競合を確認する |

基板左右にある`7`、`8`、`9`の同名端子はそれぞれ基板内部で接続されています。別々のGPIOとして割り当ててはいけません。

## 周辺機能と競合

| 機能 | 使用端子・資源 | 注意 |
|---|---|---|
| 基板上LED | PC0 / D2 | アクティブHigh |
| I2C候補 | PC1=SDA、PC2=SCL | OLEDの通信方式、電圧、アドレスを確認する |
| SPI1 | PC5=SCK、PC6=MOSI、PC7=MISO、PC4=SS候補 | GPIO、PWM、WS2812Bと同時に割り当てない |
| WS2812B用DMA/SPIドライバー | PC6 / D8、SPI1 MOSI、DMA1 Channel 3 | 既存PoCの方式を使う場合はPC6固定。エンコーダーS2などと競合する |
| PWM確認済み端子 | PC4 / D6 / A2 / TIM1_CH4 | SPI1 SS候補、ADC A2、振動制御と競合する |
| rv003usb | PD3=USB D+、PD4=USB D-、PD5=プルアップ制御 | USB HIDを使う間はこの3端子を一般GPIOやADCへ割り当てない |
| SWIO | PD1 / D11 | GPIO化にはデバッグ切断処理が必要。書き込み不能の危険を避けるため原則予約する |

タイマー、ADC、SPI、I2C、DMA、USBを使う場合は、GPIO番号だけでなく周辺機能資源の重複も`WIRING.md`へ記載してください。

## USBとPC側プログラム

- USB HIDが必要な場合だけ`rv003usb`を追加する
- USB記述子は用途ごとに異なるため、汎用の`usb_config.h`を推測で作らない。互換する既存演習またはPoCを1つ選び、その構成を根拠として明記する
- USBアプリケーションはワークショップ共通のテスト用VID:PID `1209:0001`へ固定する。Product文字列は演習ごと、自由制作ごとに設定する。ブートローダー`1209:B803`は変更しない
- VIDとPIDを定義または直接埋め込むコードには、`1209:0001`が世界で一意ではない共有テスト識別子であり、教育目的の試作とワークショップ内テスト以外に使用できないことを警告する
- ベンダー定義HIDでは、ファームウェアとPC側プログラムのVID、PID、Report ID、Report長、各バイトの意味を一致させる
- キーボードやマウスとして動作させる場合は、暴走時に入力を止められる設計、起動直後に入力を送らない設計、長押し抑止を検討する
- Web上の生成AIは受講者PCでのビルド、USB認識、実機動作を確認できない。未確認を「確認済み」と記載しない

## Devkitのビルド規約

成果物は`workspace/my/device1`に配置します。Devkitの起動ファイルから専用環境を開き、成果物のディレクトリで次を使用します。

```text
make          ビルド
make size     使用量の表示
make flash    UIAPduinoへの書き込み
make clean    ビルド生成物の削除
make doctor   開発環境の診断
make report   問い合わせ用レポート
```

- `Makefile`は`UIAP_PLATFORM`、`UIAP_WORKSPACE`、`UIAP_RUNTIME`をDevkitの起動環境から受け取る
- `TARGET_MCU := CH32V003`、`MCU_PACKAGE := 1`、`PREFIX := riscv-none-elf`を使用する
- 書き込みコマンドは既存演習の`FLASH_COMMAND`を維持する
- 依存ライブラリやツールチェーンを成果物へコピーしない
- `.elf`、`.bin`、`.hex`、`.map`、`.lst`などのビルド生成物を`device1.zip`へ含めない
- ビルドに成功してから、配線の目視確認、USBを外した状態での配線、書き込み、実機確認の順に進む

## 参照できる確認済み実装

必要な機能に一致するものだけを参照し、無関係な設定をコピーしません。

| 参照先 | 確認できる内容 |
|---|---|
| `workspace/exercises/00_onboard_led_blink` | 最小Makefile、PC0の基板上LED |
| `workspace/exercises/01_macro_keyboard` | PC3スイッチ、USBキーボードHID |
| `workspace/exercises/02_rotary_cursor_size` | PC6/PC7エンコーダー、Vendor-defined HID、PC側アプリ |
| `workspace/exercises/03_vibration_motor_console` | PC4振動制御、USB経由の指示 |
| `workspace/exercises/04_rotary_cursor_haptic` | エンコーダーと振動の組み合わせ |
| `workspace/poc/ws2812b8_hid_poc` | PC6固定のWS2812B駆動とUSB HID |

## 未確認として扱うもの

- 各受講者が選んだ部品の組み合わせでのGPIO割り当て
- 全部品を同時使用した場合の電源電流、信号品質、タイミング
- `PARTS_FOR_AI.md`で「未確認」と記載された電気仕様
- 既存演習にないライブラリや通信方式の、このDevkitでの動作
- 生成AIが作成した配線とプログラムの実機動作

未確認事項が安全性や実現可否に関係する場合は、プログラム生成を続けず、確認が必要な内容を質問してください。

## 情報源

- UIAP公式: https://www.uiap.jp/uiapduino/pro-micro/ch32v003/v1dot4
- UIAP公式Arduino variant: https://github.com/YuukiUmeta-UIAP/arduino_core_ch32/tree/main/variants/CH32V00x/CH32V003F4
- このDevkitの確認記録: `docs/project/70_VALIDATION_RESULTS.md`
