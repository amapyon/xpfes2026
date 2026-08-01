#!/bin/sh
set -u

. "$UIAP_DEVKIT_ROOT/scripts/lib/common.sh"

pass=0
warn=0
fail=0
ok() { pass=$((pass + 1)); printf '[PASS] %s\n' "$1"; }
warning() { warn=$((warn + 1)); printf '[WARN] %s\n' "$1"; }
bad() { fail=$((fail + 1)); printf '[FAIL] %s\n' "$1"; }

printf '%s\n' 'UIAP unified repository doctor (macOS)'
[ "${UIAP_PLATFORM-}" = mac ] && ok 'UIAP_PLATFORM=mac' || bad "UIAP_PLATFORM=${UIAP_PLATFORM-}"
[ "$(uname -m 2>/dev/null || true)" = arm64 ] && ok 'Apple Silicon arm64' || bad 'Apple Silicon arm64 is required'
[ -f "$UIAP_DEVKIT_ROOT/VERSION" ] && ok 'VERSION' || bad 'VERSION is missing'
[ -f "$UIAP_DEVKIT_ROOT/config/mac/bootstrap.lock" ] && ok 'macOS bootstrap lock' || bad 'macOS bootstrap lock is missing'
[ -x "$UIAP_RUNTIME/build-tools/bin/gmake" ] && ok 'GNU Make' || bad 'GNU Make is missing; run setup'
[ -x "$UIAP_RUNTIME/toolchain/bin/riscv-none-elf-gcc" ] && ok 'RISC-V GCC' || bad 'RISC-V GCC is missing; run setup'
[ -x "$UIAP_RUNTIME/python/bin/python3" ] && ok 'Python' || bad 'Python is missing; run setup'
[ -x "$UIAP_RUNTIME/bin/minichlink" ] && ok 'minichlink' || bad 'minichlink is missing; run setup with Xcode Command Line Tools installed'
[ -f "$UIAP_WORKSPACE/deps/ch32fun/ch32fun/ch32fun.mk" ] && ok 'ch32fun' || bad 'ch32fun is missing; run setup'
[ -f "$UIAP_WORKSPACE/deps/rv003usb/rv003usb/rv003usb.c" ] && ok 'rv003usb' || bad 'rv003usb is missing; run setup'

for exercise in 00_onboard_led_blink 01_macro_keyboard 02_rotary_cursor_size; do
    directory="$UIAP_WORKSPACE/exercises/$exercise"
    [ -f "$directory/Makefile" ] && ok "$exercise dispatcher Makefile" || bad "$exercise dispatcher Makefile is missing"
    [ -d "$directory/mac" ] && ok "$exercise macOS source" || bad "$exercise macOS source is missing"
    if [ -x "$UIAP_RUNTIME/build-tools/bin/gmake" ]; then
        (cd "$directory" && "$UIAP_RUNTIME/build-tools/bin/gmake" -n all >/dev/null 2>&1) && ok "$exercise make -n" || bad "$exercise make -n"
        (cd "$directory" && "$UIAP_RUNTIME/build-tools/bin/gmake" -n flash >/dev/null 2>&1) && ok "$exercise make -n flash" || bad "$exercise make -n flash"
    fi
done

if [ -x "$UIAP_PYTHON" ]; then
    "$UIAP_PYTHON" "$UIAP_WORKSPACE/exercises/01_macro_keyboard/mac/host/hidcheck.py" --self-test >/dev/null 2>&1 && ok 'Macro keyboard host self-test' || bad 'Macro keyboard host self-test'
    "$UIAP_PYTHON" "$UIAP_WORKSPACE/exercises/02_rotary_cursor_size/mac/host/cursor_size_host.py" --self-test >/dev/null 2>&1 && ok 'Rotary cursor host self-test' || bad 'Rotary cursor host self-test'
fi

warning 'Run make flash and make app with a connected UIAPduino to validate physical behavior.'
printf 'PASS=%s WARN=%s FAIL=%s\n' "$pass" "$warn" "$fail"
[ "$fail" -eq 0 ]
