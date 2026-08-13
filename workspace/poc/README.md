# PoC開発

このディレクトリは、主催者・開発者が作成する検証用PoCの保存場所です。受講者の自由制作は[../my/README.md](../my/README.md)に従い、`workspace/my/device1`へ保存します。

## 主催者用PoC

PoCプロジェクトは`<project-name>/`単位で管理します。次のコマンドは主催者・開発者がソースリポジトリで使用します。

```console
python tools/new_poc.py my_new_poc
```

`_poc_template/`と`tools/new_poc.py`は参加者向けDevkitには収録されません。

## 配置規則

```text
my_new_poc/
  README.md       # 目的、前提、確認方法、結果
  src/            # WindowsとmacOSで共通のソース
  win/            # Windowsだけで必要な差分（必要な場合だけ）
  mac/            # macOSだけで必要な差分（必要な場合だけ）
```

新規作成時には`win/`と`mac/`は生成されません。共通ソースを複製して両方へ置かず、まず`src/`などプロジェクト直下へ共通実装を置いてください。OS API、起動処理、ホストアプリなど避けられない差分が生じた時だけ、必要なディレクトリを追加します。

`tools/build_devkit.py`は、このディレクトリの検証済みPoCプログラムを参加者向けDevkitへ収録します。主催者専用の`_poc_template/`は除外します。各PoC直下の`win/`はWindows版だけ、`mac/`はmacOS版だけへ収録します。PoCは参考・発展用であり、`workspace/exercises/`の正式演習とは区別します。
