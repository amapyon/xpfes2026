# PoC開発

## 受講者の自由制作

受講者が作成する自由制作用プログラムは、次の固定ディレクトリを1件目から順番に使用します。

```text
my_device1/
my_device2/
my_device3/
```

ワークショップの標準目標は`my_device1`の完成です。参加者向け資料、標準コマンド、生成AI向け共通案内、講師の通常サポートには`my_device1`だけを使用します。

`my_device2`と`my_device3`は、`my_device1`を完成させた後に追加案を自力で試す場合だけ、順番に使用します。完成品は最大3件とし、`my_device4`以降は作成しません。

## 主催者用PoC

PoCプロジェクトは`<project-name>/`単位で管理します。

```console
python tools/new_poc.py my_new_poc
```

## 配置規則

```text
my_new_poc/
  README.md       # 目的、前提、確認方法、結果
  src/            # WindowsとmacOSで共通のソース
  win/            # Windowsだけで必要な差分（必要な場合だけ）
  mac/            # macOSだけで必要な差分（必要な場合だけ）
```

新規作成時には`win/`と`mac/`は生成されません。共通ソースを複製して両方へ置かず、まず`src/`などプロジェクト直下へ共通実装を置いてください。OS API、起動処理、ホストアプリなど避けられない差分が生じた時だけ、必要なディレクトリを追加します。

`tools/build_devkit.py`は`workspace/`全体を参加者向け配布対象にするため、このディレクトリのPoCプログラムと`_template/`もDevkitへ収録されます。ただし、各PoC直下の`win/`はWindows版だけ、`mac/`はmacOS版だけへ収録します。PoCは参考・発展用であり、`workspace/exercises/`の正式演習とは区別します。
