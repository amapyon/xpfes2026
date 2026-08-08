# UIAP Devkit 0.1.1 Windows版

## 修正内容

`0.1.0`の配布ZIPでは、`VERSION`が`0.1.0`、Windows bootstrap lockが`0.1.0-dev`となっていたため、`setup`が`UIAP-E133`で停止していました。`0.1.1`では両方を`0.1.1`へ統一しています。

配布ZIP作成時にも版番号を検査し、`VERSION`、対象OSのbootstrap lock、ZIPファイル名が一致しない場合は生成を中止します。

## 更新方法

1. `0.1.1`のWindows版ZIPと`.sha256`をダウンロードします。
2. 公開されたSHA-256とZIPのハッシュが一致することを確認します。
3. `0.1.0`とは別の空フォルダーへZIPを完全に展開します。
4. `start-uiap.cmd`を起動し、`setup`、`doctor`、`versions`の順に実行します。

`0.1.0`の展開先へ上書きしないでください。途中まで生成された`.state`、`runtime`、キャッシュを引き継がないことで、修正版の検証結果を明確にできます。
