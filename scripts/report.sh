#!/bin/sh
set -eu

. "$UIAP_DEVKIT_ROOT/scripts/lib/common.sh"

mkdir -p "$UIAP_DEVKIT_ROOT/logs/mac"
stamp=$(date -u '+%Y%m%dT%H%M%SZ')
out="$UIAP_DEVKIT_ROOT/logs/mac/uiap-report-${stamp}.txt"

{
    printf '%s\n' 'UIAP Devkit diagnostic report'
    printf 'Generated: %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    printf 'Devkit version: %s\n' "$(awk -F': ' '/^Version:/ {print $2}' "$UIAP_DEVKIT_ROOT/VERSION")"
    printf 'macOS: %s\n' "$(/usr/bin/sw_vers -productVersion 2>/dev/null || printf unknown)"
    printf 'Architecture: %s\n' "$(uname -m 2>/dev/null || printf unknown)"
    printf 'Devkit root: %s\n' "$(printf '%s' "$UIAP_DEVKIT_ROOT" | uiap_redact_home)"
    printf 'Workspace: %s\n' "$(printf '%s' "$UIAP_WORKSPACE" | uiap_redact_home)"
    printf '%s\n' '' '--- versions ---'
    /bin/sh "$UIAP_DEVKIT_ROOT/scripts/versions.sh" 2>&1
    printf '%s\n' '' '--- doctor ---'
    /bin/sh "$UIAP_DEVKIT_ROOT/scripts/doctor.sh" 2>&1 || true
} > "$out"

printf '[UIAP] Report created: %s\n' "$(printf '%s' "$out" | uiap_redact_home)"
printf '%s\n' 'Review the report before sharing it.'
