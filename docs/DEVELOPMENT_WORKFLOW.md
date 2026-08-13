# 開発・配布ワークフロー

## 正本の分離

| 対象 | 正本 |
|---|---|
| USB HID事前診断 | `workspace/preflight/` |
| 生成AI利用手順・共通入力 | `workspace/ai/` |
| 生成AI向け部品情報 | `workspace/parts/PARTS_FOR_AI.md` |
| 正式演習 | `workspace/exercises/` |
| PoC | `workspace/poc/` |
| Windows起動・依存定義 | `start-uiap.cmd`、`config/win/` |
| macOS起動・依存定義 | `start-uiap.command`、`config/mac/` |
| OS別補助処理 | `scripts/`内の`.ps1`／`.sh` |
| 設計・検証文書 | `docs/project/` |
| 生成ZIP | `dist/`（Git管理外） |

`workspace/`はWindows版とmacOS版の両方へ収録します。`preflight/`は両OS共通のファームウェアとhidapiホスト診断を収録します。正式演習は共通Makefileを入口にし、現在の実機検証済み実装を`win/`と`mac/`へ分けて保持します。

## 受講者の自由制作

受講者の標準作業場所は`workspace/poc/my_device1`です。追加案を自力で試す場合だけ、`my_device1`完成後に`my_device2`、`my_device3`を順番に使用できます。完成品は最大3件とし、ワークショップ資料と講師の通常サポートには`my_device1`だけを記載します。

自由制作は、生成AIがローカルファイルを直接編集する経路と、Web画面へ必要資料を添付して`my_device1.zip`を受け取る経路の両方を支援します。共通手順は`workspace/ai/README.md`を正本とし、どちらも最終的に`workspace/poc/my_device1`をPC上のDevkitでビルド・書き込み・実機確認します。

## 主催者用PoCの開始

```console
python tools/new_poc.py <project-name>
```

作成後は`workspace/poc/<project-name>/README.md`へ目的、前提、確認方法を記載し、共通コードを`src/`へ追加します。OS差分が避けられない場合だけ、プロジェクト直下へ`win/`または`mac/`を追加します。

PoCが演習として確定したら、実機検証結果を記録して`workspace/exercises/`へ移します。検証途中のPoCを正式演習として説明しません。

`workspace/poc/`は参考・発展用として参加者向けDevkitへ収録します。収録されていても正式演習への採用を意味しないため、参加者向けの必須手順は`workspace/exercises/`だけを基準にします。

## Devkitの生成

```console
python tools/build_devkit.py --target all
```

生成処理は次を行います。

1. ルートの起動ファイル、`scripts/`、`config/`、`workspace/`を収集する
2. Windows版にはWindows用スクリプトと各演習の`win/`だけを収録する
3. macOS版にはMac用スクリプトと各演習の`mac/`だけを収録する
4. PoCを収録し、PoC内の反対OS用ディレクトリだけを除外する
5. ビルド生成物の混入を検査する
6. 再現可能なZIPとSHA-256を`dist/`へ生成する

`workspace/preflight/`は両OS版へ共通収録します。配布検査では、README、ファームウェアソース、USB設定、Makefile、ホスト診断が揃っていることを確認します。

GitHub Actionsでも同じコマンドを使用します。リポジトリの生成処理とCI専用の生成処理を分けません。
