#!/bin/sh
set -eu

. "$UIAP_DEVKIT_ROOT/scripts/lib/common.sh"

[ "$#" -eq 1 ] || uiap_die 301 'Usage: flash.sh <firmware.bin>'
image=$1
[ -f "$image" ] || uiap_die 302 "Firmware image not found: $image"

minichlink="$UIAP_RUNTIME/bin/minichlink"
if grep -q 'UIAP_MINICHLINK_PLACEHOLDER=1' "$minichlink" 2>/dev/null; then
    uiap_die 203 'macOS arm64 minichlink is not installed. Run build-minichlink on the organizer validation Mac.'
fi
[ -x "$minichlink" ] || uiap_die 203 'minichlink is missing or not executable.'
if /usr/bin/xattr -p com.apple.quarantine "$minichlink" >/dev/null 2>&1; then
    uiap_die 205 'minichlink has com.apple.quarantine. Re-run build-minichlink.'
fi
/usr/bin/codesign --verify --verbose=4 "$minichlink" >/dev/null 2>&1 \
    || uiap_die 206 'minichlink code-signature verification failed. Re-run build-minichlink.'

mfile=$(/usr/bin/file "$minichlink" 2>/dev/null || true)
case "$mfile" in
    *arm64*) ;;
    *) uiap_die 204 "minichlink is not confirmed arm64: $mfile" ;;
esac

uiap_info 'Connect exactly one UIAPduino in bootloader mode (1209:B803).'
uiap_info "Writing: $image"
exec "$minichlink" -c 0x1209b803 -w "$image" flash -b
