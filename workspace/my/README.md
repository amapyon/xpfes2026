# 受講者の自由制作

このディレクトリには、受講者自身が作る物理UIデバイスだけを保存します。主催者が管理する生成AI向け資料、部品情報、検証用PoCは編集しません。

## 標準の制作場所

```text
workspace/my/device1/
```

ワークショップ資料と講師の通常サポートは`device1`だけを対象とします。`device1`を完成させた後、追加のアイデアを自力で試す場合だけ`device2`、`device3`を順番に使用できます。

## 制作を始める

Devkitの起動ファイルから専用環境を開始し、`workspace`で次を実行します。

```text
python ai/new_my_device.py
```

このコマンドは、主催者管理の`workspace/ai/MY_DEVICE_TEMPLATE`を`workspace/my/device1`へコピーします。既存の`device1`は上書きしません。

## 参照する資料

- 制作手順: `workspace/ai/README.md`
- 生成AI向け基板情報: `workspace/ai/BOARD_FOR_AI.md`
- 生成AI向け共通プロンプト: `workspace/ai/PROGRAM_GENERATION_PROMPT.md`
- 部品情報: `workspace/parts/PARTS_FOR_AI.md`

`workspace/ai`と`workspace/parts`は主催者管理の参照専用領域です。生成AIがローカルファイルを操作する場合も、編集可能範囲は`workspace/my/device1`だけに限定します。
