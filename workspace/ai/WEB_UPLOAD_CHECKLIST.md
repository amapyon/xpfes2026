# Web版生成AIへ渡すファイル

Web・手動受け渡し型で、新規作成を依頼する前に確認します。通常は`workspace`で`python ai/prepare_web_handoff.py`を実行し、生成されたものを1つだけ渡します。

## 自動作成した受け渡しパック

- [ ] Geminiでは`WEB_HANDOFF_device1/UPLOAD_THIS_FOLDER`を「Import Code」で選択した
- [ ] Copilot Coworkなどでは`WEB_HANDOFF_device1/AI_HANDOFF.zip`だけを添付した
- [ ] 上記を使えない場合は`WEB_HANDOFF_device1/AI_HANDOFF.md`だけを添付した
- [ ] 生成AIが`AI_HANDOFF_MANIFEST.md`と収録ファイルを読めたことを確認した

以下は、ツールを使用できない場合の手動確認項目です。

## 必須

- [ ] `PROGRAM_GENERATION_PROMPT.md`の今回の情報を記入した
- [ ] `BOARD_FOR_AI.md`
- [ ] `PARTS_FOR_AI.md`
- [ ] `MY_DEVICE_TEMPLATE/README.md`
- [ ] `MY_DEVICE_TEMPLATE/REQUIREMENTS.md`
- [ ] `MY_DEVICE_TEMPLATE/WIRING.md`
- [ ] `MY_DEVICE_TEMPLATE/Makefile`
- [ ] `MY_DEVICE_TEMPLATE/device1.c`
- [ ] `MY_DEVICE_TEMPLATE/funconfig.h`
- [ ] `MY_DEVICE_ZIP_CHECKLIST.md`

## 必要な場合だけ

- [ ] 参考にする演習またはPoCの必要ファイルだけ
- [ ] 文字の配線表を補助する配線図画像
- [ ] 修正時の`BUILD_ERROR.txt`
- [ ] 修正時の現在の`device1.zip`

## 添付しないもの

- [ ] Devkit全体を添付していない
- [ ] `workspace/deps`と`runtime`を添付していない
- [ ] `.elf`、`.bin`、`.hex`、`.map`などのビルド生成物を添付していない
- [ ] 個人情報、認証情報、秘密情報、不要なログを添付していない
- [ ] 関係のない演習やPoCを大量に添付していない

生成AIが必須ファイルを読めたことを確認してから、要件整理へ進みます。
