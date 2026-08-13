# Web版生成AIへ渡すファイル

Web・手動受け渡し型で、新規作成を依頼する前に確認します。

## 必須

- [ ] `PROGRAM_GENERATION_PROMPT.md`の今回の情報を記入した
- [ ] `BOARD_FOR_AI.md`
- [ ] `PARTS_FOR_AI.md`
- [ ] `PROJECT_TEMPLATE/README.md`
- [ ] `PROJECT_TEMPLATE/REQUIREMENTS.md`
- [ ] `PROJECT_TEMPLATE/WIRING.md`
- [ ] `PROJECT_TEMPLATE/Makefile`
- [ ] `PROJECT_TEMPLATE/my_device1.c`
- [ ] `PROJECT_TEMPLATE/funconfig.h`
- [ ] `MY_DEVICE_ZIP_CHECKLIST.md`

## 必要な場合だけ

- [ ] 参考にする演習またはPoCの必要ファイルだけ
- [ ] 文字の配線表を補助する配線図画像
- [ ] 修正時の`BUILD_ERROR.txt`
- [ ] 修正時の現在の`my_device1.zip`

## 添付しないもの

- [ ] Devkit全体を添付していない
- [ ] `workspace/deps`と`runtime`を添付していない
- [ ] `.elf`、`.bin`、`.hex`、`.map`などのビルド生成物を添付していない
- [ ] 個人情報、認証情報、秘密情報、不要なログを添付していない
- [ ] 関係のない演習やPoCを大量に添付していない

生成AIが必須ファイルを読めたことを確認してから、要件整理へ進みます。
