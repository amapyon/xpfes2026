#!/bin/sh
set -u

printf 'Devkit: '; awk -F': ' '/^Version:/ {print $2}' "$UIAP_DEVKIT_ROOT/VERSION"
printf 'Platform: '; awk -F': ' '/^Platform:/ {print $2}' "$UIAP_DEVKIT_ROOT/VERSION"
printf 'macOS: '; /usr/bin/sw_vers -productVersion 2>/dev/null || printf 'unknown\n'
printf 'Architecture: '; uname -m 2>/dev/null || printf 'unknown\n'

if [ -x "$UIAP_TOOLCHAIN_BIN/riscv-none-elf-gcc" ]; then "$UIAP_TOOLCHAIN_BIN/riscv-none-elf-gcc" --version | head -n 1; else printf '%s\n' 'RISC-V GCC: not installed (run setup)'; fi
if [ -x "$UIAP_RUNTIME/bin/make" ]; then "$UIAP_RUNTIME/bin/make" --version 2>/dev/null | head -n 1 || true; fi
if grep -q 'UIAP_MINICHLINK_PLACEHOLDER=1' "$UIAP_RUNTIME/bin/minichlink" 2>/dev/null; then printf '%s\n' 'minichlink: placeholder — run build-minichlink'; elif [ -x "$UIAP_RUNTIME/bin/minichlink" ]; then "$UIAP_RUNTIME/bin/minichlink" -h 2>&1 | head -n 1 || true; else printf '%s\n' 'minichlink: missing'; fi

if [ -x "${UIAP_PYTHON-}" ]; then
  "$UIAP_PYTHON" "$UIAP_DEVKIT_ROOT/scripts/python/hidapi_probe.py" 2>&1 || true
  "$UIAP_PYTHON" "$UIAP_WORKSPACE/exercises/02_rotary_cursor_size/host/cursor_size_host.py" version 2>&1 || true
  "$UIAP_PYTHON" "$UIAP_WORKSPACE/exercises/03_vibration_motor_console/host/motorctl.py" version 2>&1 || true
  "$UIAP_PYTHON" "$UIAP_WORKSPACE/exercises/04_rotary_cursor_haptic/host/cursor_size_host.py" version 2>&1 || true
else
  printf '%s\n' 'Python/hidapi: not installed (run setup)'
fi

if [ -f "$UIAP_WORKSPACE/deps/VERSIONS.md" ]; then printf '%s\n' '' 'Dependency lock:'; cat "$UIAP_WORKSPACE/deps/VERSIONS.md"; fi
