# XP祭り2026 UIAP Devkit統合開発環境

Windows 11 x64とmacOS Apple Siliconで、同じリポジトリをクローンして演習・PoCを開発するための統合環境です。旧`uiap-devkit-win64`と`uiap-devkit-macarm64`の検証済み内容を、共通の`workspace/`へ統合しています。

## クローン後の開始方法

Windowsでは`start-uiap.cmd`をダブルクリックし、専用Command Promptで次を実行します。

```console
setup
doctor
```

macOS Apple Siliconでは、ターミナルから次を実行します。初回セットアップでは書き込みツールをビルドするため、Xcode Command Line Toolsが必要です。

```console
/bin/sh start-uiap.command
setup
doctor
```

セットアップ後は、両OSで同じコマンドを使用します。

```console
cd preflight
make
make flash
make preflight

cd ../exercises/00_onboard_led_blink
make
make flash

cd ../01_macro_keyboard
make
make flash
make app

cd ../02_rotary_cursor_size
make
make flash
make app-dry-run
make app
```

`start-uiap.cmd`は`UIAP_PLATFORM=win`、`start-uiap.command`は`UIAP_PLATFORM=mac`を設定します。3演習のファームウェアは両OS共通です。`02_rotary_cursor_size`だけは、OS APIを呼ぶホストアプリケーションを`host/win`と`host/mac`から選択します。

最初に`workspace/preflight`を実行すると、USB HIDの列挙、PCとの往復通信、対象ボード、ファームウェアバージョン、MCU IDを演習前に確認できます。詳しくは[preflightのREADME](workspace/preflight/README.md)を参照してください。

## ソースの配置

```text
start-uiap.cmd      # Windows起動
start-uiap.command  # macOS起動
config/
  win/              # Windows依存関係ロック
  mac/              # macOS依存関係ロック
scripts/            # 両OSのsetup、doctor、補助コマンド
runtime/
  win/              # Windows setup生成物（Git管理外）
  mac/              # macOS setup生成物（Git管理外）
workspace/
  deps/              # setup生成物（Git管理外）
  preflight/         # UIAPduino USB HID事前診断
  exercises/         # 正式演習
    <exercise>/
      Makefile       # 共通ビルド入口
      <source>.c     # 共通化できる場合は直下へ配置
      win/           # OS差が必要な場合だけ
      mac/           # OS差が必要な場合だけ
  poc/
    _template/       # PoC作成用テンプレート
    <project>/       # PoCプロジェクト
docs/
  project/           # 設計、規約、検証履歴
tools/
  build_devkit.py
  new_poc.py
tests/
.github/workflows/
```

演習とPoCはリポジトリ直下の`workspace/`を正本とします。OSによる実装差がないソースは演習直下へ置き、実装差が必要な場合だけ`win/`と`mac/`へ分けます。

PoCは`workspace/poc/<project-name>/`へ追加します。プロジェクト内の共通ファイルは直下へ置き、どうしても異なる実装だけを`win/`、`mac/`へ分けます。配布時は対象OS側のディレクトリだけがそのDevkitへ入ります。

```console
python tools/new_poc.py my_new_poc
```

## 配布キットの生成

Python 3.11以降で実行します。外部パッケージは不要です。

```console
python tools/build_devkit.py --target all
```

生成物は`dist/`へ出力されます。

- `uiap-devkit-win64-<version>.zip`
- `uiap-devkit-macarm64-<version>.zip`
- 各ZIPの`.sha256`
- `SHA256SUMS`

個別に作る場合は`--target win`または`--target mac`を指定します。版番号はルートの`VERSION`を更新するか、検証用に`--version`で指定します。

```console
python tools/build_devkit.py --target win --version 0.7.0-test1
python tools/build_devkit.py --target mac --version 0.3.0-test1
```

GitHub Actionsの`Build participant kits`は、Windows runnerでWindows版、macOS runnerでMac版を検査・生成し、ダウンロード可能なArtifactとして保存します。手動実行にも対応しています。

## 演習ソースの統合状態

3演習のファームウェアとビルド設定は単一の共通実装へ統合しています。`02_rotary_cursor_size`のポインター設定処理だけはOS APIが異なるため、演習内の`host/win`と`host/mac`へ分離します。

文書の一覧は[docs/README.md](docs/README.md)、詳細な統合仕様は[99_FULL_PROJECT_GUIDE.md](docs/project/99_FULL_PROJECT_GUIDE.md)を参照してください。
