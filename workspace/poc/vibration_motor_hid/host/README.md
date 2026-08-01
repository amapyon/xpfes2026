# Host utility

`motorctl.py`はVendor-defined HID Feature Reportを使い、振動レベル`0`～`100`を送受信します。

UIAP Devkit同梱のPythonとhidapiを使用してください。システムPythonやPoC専用の仮想環境は使用しません。

```sh
make host
make doctor
make list
make on 50
make status
make off
make play PATTERN='100:0.1,0:0.4'
```

macOSでは`start-uiap.command`からDevkitを起動してください。`make doctor`はPythonがApple Silicon `arm64`で動作していることも確認します。
