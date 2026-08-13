# Workspace

このディレクトリが、演習、受講者の自由制作、PoC、主催者提供資料の正本です。Windows版とmacOS版のDevkitへ自動的に収録されます。

- `exercises/`: 当日の正式な演習
- `ai/`: 自由制作で生成AIを使う共通手順
- `my/`: 受講者自身が編集する自由制作。標準作業場所は`my/device1`
- `poc/`: 検証中または実験用のPoC
- `parts/`: 主催者が提示する生成AI向け部品情報
- `preflight/`: 演習開始前にUIAPduinoのUSB HID通信を確認する事前診断

ビルド生成物、セットアップ済みランタイム、実行ログはコミットしません。

事前診断の実行方法は[preflight/README.md](preflight/README.md)を参照してください。
