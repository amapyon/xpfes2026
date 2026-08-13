# 自由制作で生成AIを使う方法

受講者のPCには、Windows版またはmacOS版のDevkit一式がセットアップ済みであることを前提とします。生成AIの利用方法は、製品名ではなく、ローカルファイルを直接操作できるかどうかで次の2経路に分けます。

| 経路 | 生成AIの能力 | プログラムの受け渡し |
|---|---|---|
| ローカル操作型 | Devkit内のファイルを読み、`workspace/my/device1`を直接編集できる | 生成AIがローカルファイルを作成・修正する |
| Web・手動受け渡し型 | 添付したファイルだけを参照できる | 生成AIから`device1.zip`を受け取り、受講者が展開する |

どちらの経路でも、要件、配線、安全確認、完成するプログラムの配置、ビルド・書き込み・実機確認の基準は同じです。

## 収録ファイル

| ファイル | 用途 |
|---|---|
| `BOARD_FOR_AI.md` | 基板、端子、電源、周辺機能、競合、ビルド条件 |
| `PROGRAM_GENERATION_PROMPT.md` | ローカル操作型とWeb型で共通使用する生成指示 |
| `MY_DEVICE_TEMPLATE/` | `device1`の要件、配線、Cプログラム、Makefileのひな型 |
| `new_my_device.py` | ひな型を`workspace/my/device1`へ安全にコピーする初期化ツール |
| `WEB_UPLOAD_CHECKLIST.md` | Web型で生成AIへ渡すファイルの確認 |
| `MY_DEVICE_ZIP_CHECKLIST.md` | Web型で受け取ったZIPの構造と内容の確認 |
| `BUILD_ERROR_TEMPLATE.txt` | ビルド・書き込み・実機エラーを生成AIへ返す書式 |

## 共通の制作手順

1. 生成AIと相談し、作りたいものと完成条件を`workspace/my/device1/REQUIREMENTS.md`へ整理する
2. 使用する部品を`workspace/parts/PARTS_FOR_AI.md`から選ぶ
3. 配線表と安全確認結果を`workspace/my/device1/WIRING.md`へ整理する
4. 電圧、電流、端子、GPIO、ADC、PWM、タイマー、USBとの競合を確認する
5. 安全確認が終わるまで実物を配線しない
6. `workspace/my/device1`のプログラム一式を生成する
7. PC上のDevkitでビルドする
8. 配線を再確認してから書き込み、実機動作を確認する
9. エラーや動作結果を生成AIへ返し、修正する

配線図を画像で作成する場合は`WIRING.png`などとして添付できますが、`WIRING.md`の文字による配線表を正本とします。画像だけを根拠にプログラムを作らせません。

## 生成AIへ渡す共通資料

プログラム生成時には、次を生成AIへ渡します。

- `workspace/parts/PARTS_FOR_AI.md`
- `workspace/ai/BOARD_FOR_AI.md`
- 受講者と生成AIが整理した`workspace/my/device1/REQUIREMENTS.md`
- 安全確認済みの`workspace/my/device1/WIRING.md`と、必要に応じて配線図画像
- `workspace/ai/MY_DEVICE_TEMPLATE/`
- `workspace/ai/PROGRAM_GENERATION_PROMPT.md`

新規作成時は、Devkit環境の`workspace`で次を実行し、`MY_DEVICE_TEMPLATE`を`workspace/my/device1`へコピーします。既存の`device1`は上書きしません。

```text
python ai/new_my_device.py
```

Web経路で添付するファイルは`WEB_UPLOAD_CHECKLIST.md`、受け取った成果物は`MY_DEVICE_ZIP_CHECKLIST.md`で確認します。エラーを生成AIへ返すときは`BUILD_ERROR_TEMPLATE.txt`をコピーして記入します。

必要な場合だけ、参考にする演習またはPoCのファイルを追加します。Devkit全体、個人情報、認証情報、秘密情報、不要なログはWebサービスへアップロードしません。

## ローカル操作型

生成AIには次を指示します。

- `PARTS_FOR_AI.md`と`BOARD_FOR_AI.md`を参照専用で読む
- `REQUIREMENTS.md`と`WIRING.md`に従う
- 編集範囲を`workspace/my/device1`に限定する
- `workspace/parts`、`workspace/exercises`、`workspace/deps`を変更しない
- 作成後にローカル環境でビルドし、結果を確認する
- 実機確認していないことを確認済みと記載しない

## Web・手動受け渡し型

### 1. ファイルを添付する

共通資料をプロンプトと一緒に添付します。生成AIが添付資料を読めたことを確認してから、プログラム生成へ進みます。

### 2. `device1.zip`を生成する

生成AIには、完成ファイルを次の構成で出力させます。

```text
device1/
├── README.md
├── REQUIREMENTS.md
├── WIRING.md
├── WIRING.png          # 配線図画像がある場合だけ
├── Makefile
├── <main-source>.c
├── funconfig.h
├── usb_config.h        # USBを使用する場合
└── host/               # PC側プログラムが必要な場合
    ├── README.md
    └── <host-program>.py
```

ZIPにはソース一式を省略せず収録し、ビルド生成物、Devkit本体、依存ライブラリ、添付した主催者資料を複製しません。生成AIがZIPを作成できない場合は、ファイル名と完成した全文を1ファイルずつ出力させます。差分や一部の置換指示だけを初心者向け標準手順にしません。

### 3. PCへ配置する

ダウンロードしたZIPを展開し、内容が次の位置になるよう配置します。

```text
workspace/my/device1/README.md
workspace/my/device1/Makefile
```

次のような二重ディレクトリにしません。

```text
workspace/my/device1/device1/README.md
```

### 4. PC上のDevkitで確認する

Web上の生成AIは、受講者のPC上でビルド、書き込み、実機確認を完了したとは扱いません。Devkitの起動ファイルから環境を開始し、`workspace/my/device1`へ移動して、生成されたREADMEの手順に従います。

### 5. エラーを返して修正する

失敗した場合は、次を生成AIへ渡します。

- 現在の`device1.zip`
- `BUILD_ERROR_TEMPLATE.txt`をコピーし、エラー全文を保存した`BUILD_ERROR.txt`
- `device1/REQUIREMENTS.md`
- `device1/WIRING.md`
- 修正依頼

修正時も、変更箇所だけではなく修正版`device1.zip`一式を生成させ、旧版と混在させません。

## 共通の完成条件

- 成果物が`workspace/my/device1`にある
- `REQUIREMENTS.md`と`WIRING.md`が`device1`に含まれる
- `README.md`に目的、使用部品、配線、ビルド、書き込み、確認方法がある
- `WIRING.md`とプログラムのGPIO割り当てが一致する
- 未確認の部品仕様を推測で確定していない
- PC上のDevkitでビルドに成功する
- 配線の目視確認後に書き込みを行う
- 期待する実機動作を受講者自身が確認する
