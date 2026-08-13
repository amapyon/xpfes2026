# my_device1.zip確認表

Web版生成AIから受け取った成果物を、Devkitへ配置する前に確認します。

## ZIP構造

- [ ] ZIP直下に`my_device1/`が1つある
- [ ] `my_device1/my_device1/`という二重ディレクトリではない
- [ ] 展開後に`workspace/poc/my_device1/README.md`となる

## 必須ファイル

- [ ] `README.md`
- [ ] `REQUIREMENTS.md`
- [ ] `WIRING.md`
- [ ] `Makefile`
- [ ] `my_device1.c`
- [ ] `funconfig.h`

## 内容

- [ ] 使用部品がPART番号と数量で記載されている
- [ ] `WIRING.md`の基板表記とch32fun端子名が対応している
- [ ] プログラムのGPIO定義が`WIRING.md`と一致する
- [ ] 電源、信号電圧、極性、抵抗、補助回路が確認されている
- [ ] USB使用時はPD3、PD4、PD5が他用途と競合していない
- [ ] PC側プログラム使用時はUSB Report仕様が一致している
- [ ] 起動時と異常時の安全な出力状態が定義されている
- [ ] READMEにビルド、書き込み、実機確認、停止方法、未確認事項がある

## 含めないもの

- [ ] `.elf`、`.bin`、`.hex`、`.map`、`.lst`がない
- [ ] `workspace/deps`、`runtime`、Devkit本体の複製がない
- [ ] `BOARD_FOR_AI.md`、`PARTS_FOR_AI.md`など主催者資料の複製がない
- [ ] 個人情報、認証情報、秘密情報がない

## PC上での確認

- [ ] 旧`workspace/poc/my_device1`と混在させず配置した
- [ ] Devkit環境で`make`に成功した
- [ ] `make size`に成功した
- [ ] USBを外した状態で配線を目視確認した
- [ ] `WIRING.md`の配線安全確認を`確認済み`にした
- [ ] 書き込み後、受け入れ条件を実機で確認した
