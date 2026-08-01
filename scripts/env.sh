#!/bin/sh
# shellcheck shell=sh

# このファイルはsourceして使用する。
# POSIX shではsourceされたファイル内の$0は呼び出し元を示すため、
# env.sh自身の場所を$0から計算してはならない。
if [ -z "${UIAP_DEVKIT_ROOT-}" ]; then
    printf '%s\n' '[UIAP-E100] UIAP_DEVKIT_ROOT is not set.' >&2
    printf '%s\n' 'Start the Devkit with start-uiap.command.' >&2
    return 100 2>/dev/null || exit 100
fi

if [ ! -d "$UIAP_DEVKIT_ROOT" ]; then
    printf '[UIAP-E100] Devkit root does not exist: %s\n' "$UIAP_DEVKIT_ROOT" >&2
    return 100 2>/dev/null || exit 100
fi

UIAP_DEVKIT_ROOT=$(CDPATH= cd -- "$UIAP_DEVKIT_ROOT" && pwd -P)
export UIAP_DEVKIT_ROOT
export UIAP_PLATFORM=mac
export UIAP_WORKSPACE="$UIAP_DEVKIT_ROOT/workspace"
export UIAP_RUNTIME="$UIAP_DEVKIT_ROOT/runtime/mac"
export UIAP_TOOLCHAIN_BIN="$UIAP_RUNTIME/toolchain/bin"
export UIAP_FIRMWARE="$UIAP_DEVKIT_ROOT/firmware"
export UIAP_PYTHON="$UIAP_RUNTIME/python/bin/python3"

# Devkit内を先にし、ユーザーのHomebrewや別ツールチェーンを暗黙利用しない。
export PATH="$UIAP_DEVKIT_ROOT/scripts/bin:$UIAP_RUNTIME/bin:$UIAP_RUNTIME/python/bin:$UIAP_TOOLCHAIN_BIN:/usr/bin:/bin:/usr/sbin:/sbin"

unset PYTHONHOME PYTHONPATH
