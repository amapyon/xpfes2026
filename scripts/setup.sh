#!/bin/sh
set -eu

. "$UIAP_DEVKIT_ROOT/scripts/lib/common.sh"

MAKE_VERSION='4.4.1'
MAKE_BOTTLE_REVISION='1'
# Homebrew official arm64 bottles. setup chooses the minimum compatible OS bottle.
MAKE_BOTTLE_SEQUOIA_SHA256='f361639a5ec1a9355e12f985c511dd6631b6790452a52057032a3a07a690ca4e'
MAKE_BOTTLE_TAHOE_SHA256='c46713c2347b3af91fc3fb41f215f26341fec6df4687af080e55d921858f06d5'
MAKE_SOURCE_SHA256='8814ba072182b605d156d7589c19a43b89fc58ea479b9355146160946f8cf6e9'

TOOLCHAIN_VERSION='14.2.0-3'
TOOLCHAIN_ARCHIVE="xpack-riscv-none-elf-gcc-${TOOLCHAIN_VERSION}-darwin-arm64.tar.gz"
TOOLCHAIN_URL="https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases/download/v${TOOLCHAIN_VERSION}/${TOOLCHAIN_ARCHIVE}"
TOOLCHAIN_SHA256='e76e86b8c500f8e92b3b4ff7b0444cfbf3b218515f322929e0744ec3b9ed80a8'

CH32FUN_COMMIT='1e4887e11d4bfa739ed5604524b69f5be9f9275b'
CH32FUN_URL="https://github.com/cnlohr/ch32fun/archive/${CH32FUN_COMMIT}.tar.gz"
CH32FUN_SHA256='37a507fa58710a14dbd3e959def57b02a6b0b1d410c9e307653e22aeb081ba9f'
RV003USB_COMMIT='75d926abe89a3002020b989015eab97ce5ad0470'
RV003USB_URL="https://github.com/cnlohr/rv003usb/archive/${RV003USB_COMMIT}.tar.gz"

PYTHON_VERSION='3.10.20'
PYTHON_PBS_RELEASE='20260728'
PYTHON_ARCHIVE="cpython-${PYTHON_VERSION}+${PYTHON_PBS_RELEASE}-aarch64-apple-darwin-install_only_stripped.tar.gz"
PYTHON_URL="https://github.com/astral-sh/python-build-standalone/releases/download/${PYTHON_PBS_RELEASE}/cpython-${PYTHON_VERSION}%2B${PYTHON_PBS_RELEASE}-aarch64-apple-darwin-install_only_stripped.tar.gz"
PYTHON_SHA256='e070282def280622010326056a7fdc4a95ac588ae69611a0f2dfd333dbb91b4f'
HIDAPI_VERSION='0.15.0'
HIDAPI_WHEEL='hidapi-0.15.0-cp310-cp310-macosx_11_0_arm64.whl'
HIDAPI_URL='https://files.pythonhosted.org/packages/2d/97/bcbcb89f9461c29d3b12dd32affd29e6312fd521154ee7f394496d0039a9/hidapi-0.15.0-cp310-cp310-macosx_11_0_arm64.whl'
HIDAPI_SHA256='1fa3e792987d4b7ed66d785491307e23d4f09d3636f8a23665a9694c43e92409'

uiap_require_arm64
major=$(uiap_macos_major)
[ -n "$major" ] || uiap_die 102 'Could not determine the macOS version.'
[ "$major" -ge 15 ] || uiap_die 102 "macOS 15 or later is required; detected major version: $major"

mkdir -p "$UIAP_RUNTIME/downloads" "$UIAP_RUNTIME/toolchain" "$UIAP_RUNTIME/build-tools/bin" "$UIAP_RUNTIME/python" "$UIAP_RUNTIME/bin" "$UIAP_WORKSPACE/deps" "$UIAP_DEVKIT_ROOT/.state/mac"
cp "$UIAP_DEVKIT_ROOT/scripts/bin/make" "$UIAP_RUNTIME/bin/make"
chmod 0755 "$UIAP_RUNTIME/bin/make"

fetch() {
    url=$1
    output=$2
    if [ -f "$output" ]; then
        uiap_info "Using cached download: $(basename "$output")"
        return 0
    fi
    uiap_info "Downloading: $url"
    tmp="${output}.part"
    rm -f "$tmp"
    /usr/bin/curl --fail --location --retry 3 --retry-delay 2 --output "$tmp" "$url"
    mv "$tmp" "$output"
}

fetch_ghcr_blob() {
    repository=$1
    digest=$2
    output=$3
    if [ -f "$output" ]; then
        uiap_info "Using cached download: $(basename "$output")"
        return 0
    fi

    token_url="https://ghcr.io/token?service=ghcr.io&scope=repository:${repository}:pull"
    uiap_info "Requesting anonymous GHCR download token for: ${repository}"
    token_json=$(/usr/bin/curl --fail --silent --show-error --location --retry 3 --retry-delay 2 "$token_url")
    token=$(printf '%s' "$token_json" | /usr/bin/sed -n 's/.*"token":"\([^"]*\)".*/\1/p')
    [ -n "$token" ] || uiap_die 108 "Could not obtain a GHCR token for ${repository}."

    url="https://ghcr.io/v2/${repository}/blobs/sha256:${digest}"
    uiap_info "Downloading pinned Homebrew bottle: $url"
    tmp="${output}.part"
    rm -f "$tmp"
    /usr/bin/curl --fail --location --retry 3 --retry-delay 2 \
        --header "Authorization: Bearer ${token}" \
        --output "$tmp" "$url"
    mv "$tmp" "$output"
}

validate_tar_paths() {
    archive=$1
    if /usr/bin/tar -tzf "$archive" | /usr/bin/awk '
        BEGIN { bad = 0 }
        /^\// { bad = 1 }
        /(^|\/)\.\.(\/|$)/ { bad = 1 }
        /\\/ { bad = 1 }
        END { exit bad ? 0 : 1 }
    '; then
        uiap_die 105 "Unsafe path detected in archive: $archive"
    fi
}

extract_single_root() {
    archive=$1
    output=$2
    temp=$3
    validate_tar_paths "$archive"
    rm -rf "$temp"
    mkdir -p "$temp"
    /usr/bin/tar -xzf "$archive" -C "$temp"
    roots=$(find "$temp" -mindepth 1 -maxdepth 1 -type d -print)
    root_count=$(printf '%s\n' "$roots" | /usr/bin/awk 'NF { count++ } END { print count + 0 }')
    [ "$root_count" -eq 1 ] || uiap_die 106 "Archive must contain exactly one top-level directory: $archive"
    if find "$temp" -mindepth 1 -maxdepth 1 ! -type d -print -quit | grep . >/dev/null 2>&1; then
        uiap_die 106 "Archive contains an unexpected top-level file: $archive"
    fi
    root=$(printf '%s\n' "$roots" | head -n 1)
    rm -rf "$output"
    mv "$root" "$output"
    rm -rf "$temp"
}

# 1. Pinned GNU Make arm64 bottle.
# macOS 15 uses the Sequoia bottle. macOS 26 and later use the Tahoe bottle.
if [ "$major" -ge 26 ]; then
    make_os_tag='arm64_tahoe'
    make_bottle_sha256=$MAKE_BOTTLE_TAHOE_SHA256
else
    make_os_tag='arm64_sequoia'
    make_bottle_sha256=$MAKE_BOTTLE_SEQUOIA_SHA256
fi
make_archive="make-${MAKE_VERSION}-${MAKE_BOTTLE_REVISION}-${make_os_tag}.bottle.tar.gz"
make_archive_path="$UIAP_RUNTIME/downloads/$make_archive"
fetch_ghcr_blob 'homebrew/core/make' "$make_bottle_sha256" "$make_archive_path"
actual=$(uiap_sha256 "$make_archive_path")
if [ "$actual" != "$make_bottle_sha256" ]; then
    rm -f "$make_archive_path"
    uiap_die 109 "GNU Make bottle SHA-256 mismatch. Expected $make_bottle_sha256; got $actual"
fi
uiap_info 'GNU Make bottle SHA-256: PASS'
validate_tar_paths "$make_archive_path"
make_temp="$UIAP_DEVKIT_ROOT/.state/make-extract"
rm -rf "$make_temp"
mkdir -p "$make_temp"
/usr/bin/tar -xzf "$make_archive_path" -C "$make_temp"
make_candidate=$(find "$make_temp" -type f -path '*/bin/gmake' -print -quit)
[ -n "$make_candidate" ] || uiap_die 110 'GNU Make bottle did not contain bin/gmake.'
cp "$make_candidate" "$UIAP_RUNTIME/build-tools/bin/gmake"
chmod 0755 "$UIAP_RUNTIME/build-tools/bin/gmake"
rm -rf "$make_temp"

make_file=$(/usr/bin/file "$UIAP_RUNTIME/build-tools/bin/gmake" 2>/dev/null || true)
case "$make_file" in
    *arm64*) : ;;
    *) uiap_die 111 "Bundled GNU Make is not arm64: $make_file" ;;
esac
make_links=$(/usr/bin/otool -L "$UIAP_RUNTIME/build-tools/bin/gmake" 2>/dev/null | /usr/bin/tail -n +2 || true)
if printf '%s\n' "$make_links" | /usr/bin/grep -E '/opt/homebrew/|/Users/' >/dev/null 2>&1; then
    uiap_die 112 'GNU Make has a Homebrew or developer-specific dynamic-library dependency.'
fi
"$UIAP_RUNTIME/build-tools/bin/gmake" --version >/dev/null 2>&1 || uiap_die 113 'Bundled GNU Make could not start.'
uiap_info "GNU Make: $("$UIAP_RUNTIME/build-tools/bin/gmake" --version | /usr/bin/head -n 1)"

# 2. Verified arm64 toolchain.
toolchain_archive="$UIAP_RUNTIME/downloads/$TOOLCHAIN_ARCHIVE"
fetch "$TOOLCHAIN_URL" "$toolchain_archive"
actual=$(uiap_sha256 "$toolchain_archive")
if [ "$actual" != "$TOOLCHAIN_SHA256" ]; then
    rm -f "$toolchain_archive"
    uiap_die 104 "Toolchain SHA-256 mismatch. Expected $TOOLCHAIN_SHA256; got $actual"
fi
uiap_info 'Toolchain SHA-256: PASS'
if [ ! -x "$UIAP_RUNTIME/toolchain/bin/riscv-none-elf-gcc" ]; then
    extract_single_root "$toolchain_archive" "$UIAP_RUNTIME/toolchain" "$UIAP_DEVKIT_ROOT/.state/toolchain-extract"
fi


# 3. Pinned Python arm64 runtime and hidapi wheel.
python_archive="$UIAP_RUNTIME/downloads/$PYTHON_ARCHIVE"
fetch "$PYTHON_URL" "$python_archive"
actual=$(uiap_sha256 "$python_archive")
if [ "$actual" != "$PYTHON_SHA256" ]; then
    rm -f "$python_archive"
    uiap_die 116 "Python runtime SHA-256 mismatch. Expected $PYTHON_SHA256; got $actual"
fi
uiap_info 'Python runtime SHA-256: PASS'
if [ ! -x "$UIAP_RUNTIME/python/bin/python3" ]; then
    extract_single_root "$python_archive" "$UIAP_RUNTIME/python" "$UIAP_DEVKIT_ROOT/.state/python-extract"
fi
python_file=$(/usr/bin/file -L "$UIAP_RUNTIME/python/bin/python3" 2>/dev/null || true)
case "$python_file" in
    *arm64*) : ;;
    *) uiap_die 117 "Bundled Python is not arm64: $python_file" ;;
esac

hidapi_wheel="$UIAP_RUNTIME/downloads/$HIDAPI_WHEEL"
fetch "$HIDAPI_URL" "$hidapi_wheel"
actual=$(uiap_sha256 "$hidapi_wheel")
if [ "$actual" != "$HIDAPI_SHA256" ]; then
    rm -f "$hidapi_wheel"
    uiap_die 118 "hidapi wheel SHA-256 mismatch. Expected $HIDAPI_SHA256; got $actual"
fi
uiap_info 'hidapi wheel SHA-256: PASS'
"$UIAP_RUNTIME/python/bin/python3" -m pip --disable-pip-version-check install --no-index --no-deps --force-reinstall "$hidapi_wheel" >/dev/null || uiap_die 119 'Could not install the pinned hidapi wheel into the Devkit Python runtime.'
"$UIAP_RUNTIME/python/bin/python3" "$UIAP_DEVKIT_ROOT/scripts/python/hidapi_probe.py" >/dev/null || uiap_die 120 'Bundled Python/hidapi probe failed.'
uiap_info 'Bundled Python/hidapi: PASS'

# 4. Pinned ch32fun source and test-only subset.
ch32_archive="$UIAP_RUNTIME/downloads/ch32fun-${CH32FUN_COMMIT}.tar.gz"
fetch "$CH32FUN_URL" "$ch32_archive"
ch32_hash=$(uiap_sha256 "$ch32_archive")
if [ "$ch32_hash" != "$CH32FUN_SHA256" ]; then
    rm -f "$ch32_archive"
    uiap_die 114 "ch32fun SHA-256 mismatch. Expected $CH32FUN_SHA256; got $ch32_hash"
fi
uiap_info 'ch32fun archive SHA-256: PASS'
printf 'ch32fun %s %s\n' "$CH32FUN_COMMIT" "$ch32_hash" > "$UIAP_DEVKIT_ROOT/.state/source-archive-hashes.txt"
ch32_full="$UIAP_DEVKIT_ROOT/.state/ch32fun-full"
extract_single_root "$ch32_archive" "$ch32_full" "$UIAP_DEVKIT_ROOT/.state/ch32fun-extract"
if find "$ch32_full" -type l -print -quit | grep . >/dev/null 2>&1; then
    uiap_die 107 'ch32fun source archive contains a symbolic link; refusing test subset generation.'
fi
rm -rf "$UIAP_WORKSPACE/deps/ch32fun"
mkdir -p "$UIAP_WORKSPACE/deps/ch32fun/misc" "$UIAP_WORKSPACE/deps/ch32fun/extralibs"
cp "$ch32_full/LICENSE" "$UIAP_WORKSPACE/deps/ch32fun/LICENSE"
cp "$ch32_full/README.md" "$UIAP_WORKSPACE/deps/ch32fun/README.md"
cp -R "$ch32_full/ch32fun" "$UIAP_WORKSPACE/deps/ch32fun/ch32fun"
# Remove the non-portable NEWLIB include option; the xPack compiler resolves
# its own target headers.  Upstream uses -I$(NEWLIB), not a literal path.
ch32fun_mk="$UIAP_WORKSPACE/deps/ch32fun/ch32fun/ch32fun.mk"
ch32fun_mk_tmp="$ch32fun_mk.uiap-tmp"
/usr/bin/awk 'index($0, "-I$(NEWLIB)") == 0 { print }' "$ch32fun_mk" > "$ch32fun_mk_tmp"
/bin/mv "$ch32fun_mk_tmp" "$ch32fun_mk"
if /usr/bin/grep -F -- '-I$(NEWLIB)' "$ch32fun_mk" >/dev/null 2>&1; then
    uiap_die 115 'Could not remove the non-portable ch32fun NEWLIB include option.'
fi
cp "$ch32_full/misc/libgcc.a" "$UIAP_WORKSPACE/deps/ch32fun/misc/libgcc.a"
printf '%s\n' "$CH32FUN_COMMIT" > "$UIAP_WORKSPACE/deps/ch32fun/UPSTREAM_COMMIT"
(
    cd "$UIAP_WORKSPACE/deps/ch32fun"
    find . -type f ! -name ALLOWLIST.txt -print | sed 's#^./##' | LC_ALL=C sort > ALLOWLIST.txt
)
cat > "$UIAP_WORKSPACE/deps/ch32fun/SUBSET.md" <<EOF
# ch32fun test subset

Upstream commit: $CH32FUN_COMMIT
Archive SHA-256 observed during setup: $ch32_hash

This test subset copies the complete upstream ch32fun/ directory plus misc/libgcc.a.
It is not the final pre-reviewed allowlist subset and must not be treated as release-approved.
EOF
rm -rf "$ch32_full"

# 5. Pinned rv003usb source tree.
rv_archive="$UIAP_RUNTIME/downloads/rv003usb-${RV003USB_COMMIT}.tar.gz"
fetch "$RV003USB_URL" "$rv_archive"
rv_hash=$(uiap_sha256 "$rv_archive")
printf 'rv003usb %s %s\n' "$RV003USB_COMMIT" "$rv_hash" >> "$UIAP_DEVKIT_ROOT/.state/source-archive-hashes.txt"
extract_single_root "$rv_archive" "$UIAP_WORKSPACE/deps/rv003usb" "$UIAP_DEVKIT_ROOT/.state/rv003usb-extract"
if find "$UIAP_WORKSPACE/deps/rv003usb" -type l -print -quit | grep . >/dev/null 2>&1; then
    uiap_die 107 'rv003usb source archive contains a symbolic link; refusing dependency installation.'
fi
printf '%s\n' "$RV003USB_COMMIT" > "$UIAP_WORKSPACE/deps/rv003usb/UPSTREAM_COMMIT"

cat > "$UIAP_WORKSPACE/deps/VERSIONS.md" <<EOF
# Dependency versions

| Component | Version or commit | Setup-observed archive SHA-256 | Status |
|---|---|---|---|
| GNU Make | $MAKE_VERSION | $make_bottle_sha256 | Homebrew arm64 bottle; expected hash pinned |
| xPack GNU RISC-V Embedded GCC | $TOOLCHAIN_VERSION | $TOOLCHAIN_SHA256 | Expected hash pinned |
| ch32fun | $CH32FUN_COMMIT | $ch32_hash | Expected hash pinned |
| rv003usb | $RV003USB_COMMIT | $rv_hash | Hash observed, not release-pinned |
| minichlink | not bundled | n/a | Release blocker |
| Python | $PYTHON_VERSION | $PYTHON_SHA256 | python-build-standalone $PYTHON_PBS_RELEASE; arm64 |
| hidapi | $HIDAPI_VERSION | $HIDAPI_SHA256 | CPython 3.10 macOS arm64 wheel |
| macOS cursor host | Python source | source in exercise 02 | Runs with bundled Python/hidapi; no host compilation |
EOF

cat > "$UIAP_DEVKIT_ROOT/.state/mac/setup-complete" <<EOF
version=0.1.0-dev
date=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
EOF

if [ ! -x "$UIAP_RUNTIME/bin/minichlink" ] || /usr/bin/grep -q 'UIAP_MINICHLINK_PLACEHOLDER=1' "$UIAP_RUNTIME/bin/minichlink" 2>/dev/null; then
    uiap_info 'Building the pinned macOS arm64 minichlink write tool.'
    /bin/sh "$UIAP_DEVKIT_ROOT/scripts/build-minichlink.sh"
fi

uiap_info 'Online setup completed.'
uiap_info 'Exercise 02 uses the bundled Python/hidapi host; build-host-tools is no longer required.'
uiap_info 'Run: doctor'
