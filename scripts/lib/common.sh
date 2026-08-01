#!/bin/sh
# shellcheck shell=sh

uiap_die() {
    code=$1
    shift
    printf '[UIAP-E%s] %s\n' "$code" "$*" >&2
    exit "$code"
}

uiap_warn() {
    code=$1
    shift
    printf '[UIAP-W%s] %s\n' "$code" "$*" >&2
}

uiap_info() {
    printf '[UIAP] %s\n' "$*"
}

uiap_sha256() {
    /usr/bin/shasum -a 256 "$1" | /usr/bin/awk '{print $1}'
}

uiap_require_arm64() {
    arch=$(uname -m 2>/dev/null || true)
    [ "$arch" = arm64 ] || uiap_die 101 "Apple Silicon arm64 is required; detected: ${arch:-unknown}"
}

uiap_macos_major() {
    /usr/bin/sw_vers -productVersion 2>/dev/null | /usr/bin/awk -F. '{print $1}'
}

uiap_redact_home() {
    /usr/bin/sed "s#${HOME}#~#g"
}
