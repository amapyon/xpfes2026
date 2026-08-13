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

cd ../03_vibration_motor_console
make
make flash
make pulse

cd ../04_rotary_cursor_haptic
make
make flash
make app-dry-run
make app
```

`start-uiap.cmd`は`UIAP_PLATFORM=win`、`start-uiap.command`は`UIAP_PLATFORM=mac`を設定します。5演習のファームウェアは両OS共通です。`02_rotary_cursor_size`は振動なしのカーソルサイズ変更、`03_vibration_motor_console`は振動モジュールを配線してMakeコマンドから単体操作、`04_rotary_cursor_haptic`は両方を組み合わせる演習です。`02`と`04`は、それぞれ単一の`host/cursor_size_host.py`が実行時にOSバックエンドを選択します。

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
  ai/                # 自由制作で生成AIを使う共通手順
  my/                # 受講者が編集する自由制作
  deps/              # setup生成物（Git管理外）
  preflight/         # UIAPduino USB HID事前診断
  parts/             # 生成AI向け部品情報
  exercises/         # 正式演習
    <exercise>/
      Makefile       # 共通ビルド入口
      <source>.c     # 共通化できる場合は直下へ配置
      win/           # OS差が必要な場合だけ
      mac/           # OS差が必要な場合だけ
  poc/
    _poc_template/   # 主催者用PoC作成テンプレート（配布ZIP対象外）
    <project>/       # PoCプロジェクト
docs/
  project/           # 設計、規約、検証履歴
tools/
  build_devkit.py
  new_poc.py
tests/
.github/workflows/
```

演習、受講者の自由制作、PoCはリポジトリ直下の`workspace/`を正本とします。OSによる実装差がないソースは各プロジェクト直下へ置き、実装差が必要な場合だけ`win/`と`mac/`へ分けます。

受講者の自由制作は`workspace/my/device1/`を標準作業場所とします。完成品は最大3件までとし、追加案を自力で試す場合だけ`device2/`、`device3/`を順番に使用します。ワークショップ資料と講師の通常サポートは`device1/`だけを対象とします。

Devkit環境の`workspace`で`python ai/new_my_device.py`を実行すると、受講者用ひな型から`my/device1`を作成できます。既存の`device1`は上書きしません。

自由制作を生成AIへ相談するときは、主催者が管理する`workspace/parts/PARTS_FOR_AI.md`を部品情報の正本として参照させます。未確認事項を一般的な同名部品の仕様で補わず、配線とプログラムは記載済みの条件に基づいて作成します。

生成AIがローカルファイルを直接操作できる場合と、Web画面でファイルを手動受け渡しする場合の両方を正式経路とします。入力資料と完成物の仕様は共通とし、Web経路では生成AIから`device1.zip`を受け取り、`workspace/my/device1/`へ展開してPC上のDevkitでビルドします。詳細は[workspace/ai/README.md](workspace/ai/README.md)を参照してください。

主催者用PoCは`workspace/poc/<project-name>/`へ追加します。`workspace/poc/_poc_template`と`tools/new_poc.py`は主催者用リポジトリだけで使用し、参加者向けDevkitには収録しません。検証済みのPoCは参考・発展用としてDevkitへ収録しますが、正式演習は`workspace/exercises/`と区別します。プロジェクト内の共通ファイルは直下へ置き、どうしても異なる実装だけを`win/`、`mac/`へ分けます。配布時は対象OS側のディレクトリだけがそのDevkitへ入ります。

```console
python tools/new_poc.py my_new_poc
```

## 配布キットの生成

Python 3.11以降で実行します。外部パッケージは不要です。

```console
python tools/build_devkit.py --target all
```

研修スライド作成AIへ渡す、重複を除いたドキュメントZIPは次で生成します。

```console
python tools/build_document_bundle.py
```

出力は`dist/workshop-slide-docs.zip`です。収録方針は[docs/DEVELOPMENT_WORKFLOW.md](docs/DEVELOPMENT_WORKFLOW.md)を参照してください。

生成物は`dist/`へ出力されます。

- `uiap-devkit-win64-<version>.zip`
- `uiap-devkit-macarm64-<version>.zip`
- 各ZIPの`.sha256`
- `SHA256SUMS`

個別に作る場合は`--target win`または`--target mac`を指定します。版番号はルートの`VERSION`、`config/win/bootstrap.lock.json`、`config/mac/bootstrap.lock`で同じ値に更新します。`--version`を指定する場合も`VERSION`と同じ値でなければビルドは停止します。

```console
python tools/build_devkit.py --target win
python tools/build_devkit.py --target mac
```

GitHub Actionsの`Build participant kits`は、Windows runnerでWindows版、macOS runnerでMac版を検査・生成します。各runnerでは、ZIP作成前に`VERSION`と対象OSのbootstrap lockが一致することも検査します。`VERSION`と一致する`v<version>`タグをpushするとGitHub Releaseを作成し、受講者がZIP、各ZIPの`.sha256`、`SHA256SUMS`をダウンロードできる状態で公開します。通常のpush、Pull Request、手動実行では、生成物を14日間のArtifactとして保存します。

## 演習ソースの統合状態

5演習のファームウェアとビルド設定は、それぞれ演習直下の共通実装へ統合しています。`03_vibration_motor_console`を含むホストプログラムはWindows/macOS共通です。`02_rotary_cursor_size`と`04_rotary_cursor_haptic`のポインター設定処理は、各演習の単一ホスト内でWindows/macOSバックエンドへ分離します。

文書の一覧は[docs/README.md](docs/README.md)、詳細な統合仕様は[99_FULL_PROJECT_GUIDE.md](docs/project/99_FULL_PROJECT_GUIDE.md)を参照してください。
