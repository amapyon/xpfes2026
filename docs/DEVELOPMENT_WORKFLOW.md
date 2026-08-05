# 開発・配布ワークフロー

## 正本の分離

| 対象 | 正本 |
|---|---|
| USB HID事前診断 | `workspace/preflight/` |
| 正式演習 | `workspace/exercises/` |
| PoC | `workspace/poc/` |
| Windows起動・依存定義 | `start-uiap.cmd`、`config/win/` |
| macOS起動・依存定義 | `start-uiap.command`、`config/mac/` |
| OS別補助処理 | `scripts/`内の`.ps1`／`.sh` |
| 設計・検証文書 | `docs/project/` |
| 生成ZIP | `dist/`（Git管理外） |

`workspace/`はWindows版とmacOS版の両方へ収録します。`preflight/`は両OS共通のファームウェアとhidapiホスト診断を収録します。正式演習は共通Makefileを入口にし、現在の実機検証済み実装を`win/`と`mac/`へ分けて保持します。

## PoCの開始

```console
python tools/new_poc.py <project-name>
```

作成後は`workspace/poc/<project-name>/README.md`へ目的、前提、確認方法を記載し、共通コードを`src/`へ追加します。OS差分が避けられない場合だけ、プロジェクト直下へ`win/`または`mac/`を追加します。

PoCが演習として確定したら、実機検証結果を記録して`workspace/exercises/`へ移します。検証途中のPoCを正式演習として説明しません。

## Devkitの生成

```console
python tools/build_devkit.py --target all
```

生成処理は次を行います。

1. ルートの起動ファイル、`scripts/`、`config/`、`workspace/`を収集する
2. Windows版にはWindows用スクリプトと各演習の`win/`だけを収録する
3. macOS版にはMac用スクリプトと各演習の`mac/`だけを収録する
4. PoC内の反対OS用ディレクトリを除外する
5. ビルド生成物の混入を検査する
6. 再現可能なZIPとSHA-256を`dist/`へ生成する

`workspace/preflight/`は両OS版へ共通収録します。配布検査では、README、ファームウェアソース、USB設定、Makefile、ホスト診断が揃っていることを確認します。

GitHub Actionsでも同じコマンドを使用します。リポジトリの生成処理とCI専用の生成処理を分けません。
