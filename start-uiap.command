#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)

# env.shはsourceされた側の$0から自分自身の場所を判定できないため、
# 起動ファイルが確定したDevkitルートを明示的に渡す。
export UIAP_DEVKIT_ROOT="$SCRIPT_DIR"
. "$UIAP_DEVKIT_ROOT/scripts/env.sh"

if [ ! -d "$UIAP_WORKSPACE" ]; then
    printf '%s\n' '[UIAP-E104] The workspace directory is missing.'
    printf 'Devkit root: %s\n' "$UIAP_DEVKIT_ROOT"
    printf 'Expected workspace: %s\n' "$UIAP_WORKSPACE"
    printf '%s' 'Press Enter to close... '
    read _uiap_dummy || true
    exit 104
fi

if [ "$(uname -m 2>/dev/null || true)" != "arm64" ]; then
    printf '%s\n' '[UIAP-E101] This Devkit requires Apple Silicon arm64.'
    printf 'Detected architecture: %s\n' "$(uname -m 2>/dev/null || printf unknown)"
    printf '%s\n' 'Intel Mac and Rosetta 2 execution are not supported.'
    printf '%s' 'Press Enter to close... '
    read _uiap_dummy || true
    exit 101
fi

cd "$UIAP_WORKSPACE"
/bin/sh "$UIAP_DEVKIT_ROOT/scripts/welcome.sh"

# 独自ZDOTDIRを使い、ユーザーの.zshrcへ依存しない。
# 同梱シェルスクリプトはzsh関数から/bin/shで読み込むため、
# 初回承認後に各補助スクリプトでGatekeeper警告が繰り返されにくい構成とする。
export ZDOTDIR="$UIAP_DEVKIT_ROOT/scripts/zsh"
exec /bin/zsh -i
