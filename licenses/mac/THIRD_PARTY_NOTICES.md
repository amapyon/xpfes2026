# Third-party notices — macOS test13

このZIPはオンライン初期化型の主催者検証版です。`setup`が固定済みGNU Make、RISC-V GCC、Python、hidapi、ソース依存を取得します。

公開配布前に、実際の最終ZIPを基準としてPython、hidapi、GCC、GNU Make、ch32fun、rv003usb、minichlink、libusbのライセンス本文・著作権表示・対応ソース条件を確定してください。

演習02のPythonホストは`hidapi`を使用し、カーソルサイズ変更部分ではAppleの公開SDKとして保証されていないCoreGraphics/SkyLight APIをPython `ctypes`から動的に参照します。test13は主催者実機検証用です。
