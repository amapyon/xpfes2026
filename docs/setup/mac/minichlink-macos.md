# macOS arm64 minichlink local build — test12

`build-minichlink`は主催者用Macで実行する再現ビルドです。参加者向け最終版には検証済みバイナリを同梱し、Command Line Toolsを要求しない方針です。

## 固定入力

```text
ch32fun commit: 1e4887e11d4bfa739ed5604524b69f5be9f9275b
ch32fun archive SHA-256: 37a507fa58710a14dbd3e959def57b02a6b0b1d410c9e307653e22aeb081ba9f
libusb version: 1.0.29
libusb archive SHA-256: 5977fc950f8d1395ccea9bd48c06b3f808fd3c2c961b44b0c2e6e29fc3a70a85
```

SHA-256が一致しない場合は処理を中止します。

## 実行

```sh
build-minichlink
doctor
```

処理内容:

1. 入力アーカイブを取得してSHA-256を照合
2. アーカイブパスを検査
3. libusbをarm64静的ライブラリとしてビルド
4. minichlinkをarm64でビルド
5. 動的libusb、Homebrew、開発者ホーム依存を拒否
6. 生成した`minichlink`単体の隔離属性を除去
7. アドホック署名と署名検証
8. `minichlink.build-info`へ来歴と成果物SHA-256を記録

## 書き込み確認

```sh
cd "$UIAP_WORKSPACE/exercises/00_onboard_led_blink"
make clean
make flash
```

期待結果:

```text
VID:0x1209, PID:0xb803
Detected CH32V003
Image written.
Booting
```
