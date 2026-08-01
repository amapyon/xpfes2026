#!/bin/sh
set -eu

. "$UIAP_DEVKIT_ROOT/scripts/lib/common.sh"

CH32FUN_COMMIT='1e4887e11d4bfa739ed5604524b69f5be9f9275b'
CH32FUN_ARCHIVE="ch32fun-${CH32FUN_COMMIT}.tar.gz"
CH32FUN_URL="https://github.com/cnlohr/ch32fun/archive/${CH32FUN_COMMIT}.tar.gz"
LIBUSB_VERSION='1.0.29'
LIBUSB_ARCHIVE="libusb-${LIBUSB_VERSION}.tar.bz2"
LIBUSB_URL="https://github.com/libusb/libusb/releases/download/v${LIBUSB_VERSION}/${LIBUSB_ARCHIVE}"
CH32FUN_SHA256='37a507fa58710a14dbd3e959def57b02a6b0b1d410c9e307653e22aeb081ba9f'
LIBUSB_SHA256='5977fc950f8d1395ccea9bd48c06b3f808fd3c2c961b44b0c2e6e29fc3a70a85'

uiap_require_arm64

if ! /usr/bin/xcrun --find clang >/dev/null 2>&1; then
    uiap_die 221 'Apple Command Line Tools are required on the organizer build Mac. Run: xcode-select --install'
fi
CLANG=$(/usr/bin/xcrun --find clang)
SDKROOT=$(/usr/bin/xcrun --show-sdk-path 2>/dev/null || true)
[ -n "$SDKROOT" ] || uiap_die 221 'macOS SDK was not found through xcrun.'

BUILD_ROOT="$UIAP_RUNTIME/build/minichlink-local"
DOWNLOADS="$UIAP_RUNTIME/downloads"
SRC_ROOT="$BUILD_ROOT/src"
OUT_ROOT="$BUILD_ROOT/out"
mkdir -p "$DOWNLOADS" "$SRC_ROOT" "$OUT_ROOT" "$UIAP_RUNTIME/bin" "$UIAP_DEVKIT_ROOT/.state"

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

safe_tar_check() {
    archive=$1
    mode=$2
    if [ "$mode" = bz2 ]; then
        listing=$(/usr/bin/tar -tjf "$archive")
    else
        listing=$(/usr/bin/tar -tzf "$archive")
    fi
    printf '%s\n' "$listing" | /usr/bin/awk '
        /^\// { bad=1 }
        /(^|\/)\.\.(\/|$)/ { bad=1 }
        /\\/ { bad=1 }
        END { exit bad ? 1 : 0 }
    ' || uiap_die 222 "Unsafe archive path detected: $archive"
}

CH32FUN_PATH="$DOWNLOADS/$CH32FUN_ARCHIVE"
LIBUSB_PATH="$DOWNLOADS/$LIBUSB_ARCHIVE"
fetch "$CH32FUN_URL" "$CH32FUN_PATH"
fetch "$LIBUSB_URL" "$LIBUSB_PATH"

CH32FUN_SHA=$(/usr/bin/shasum -a 256 "$CH32FUN_PATH" | /usr/bin/awk '{print $1}')
LIBUSB_SHA=$(/usr/bin/shasum -a 256 "$LIBUSB_PATH" | /usr/bin/awk '{print $1}')
if [ "$CH32FUN_SHA" != "$CH32FUN_SHA256" ]; then
    rm -f "$CH32FUN_PATH"
    uiap_die 221 "ch32fun SHA-256 mismatch. Expected $CH32FUN_SHA256; got $CH32FUN_SHA"
fi
if [ "$LIBUSB_SHA" != "$LIBUSB_SHA256" ]; then
    rm -f "$LIBUSB_PATH"
    uiap_die 221 "libusb SHA-256 mismatch. Expected $LIBUSB_SHA256; got $LIBUSB_SHA"
fi
uiap_info 'ch32fun archive SHA-256: PASS'
uiap_info 'libusb archive SHA-256: PASS'

safe_tar_check "$CH32FUN_PATH" gz
safe_tar_check "$LIBUSB_PATH" bz2
rm -rf "$SRC_ROOT"
mkdir -p "$SRC_ROOT"
/usr/bin/tar -xzf "$CH32FUN_PATH" -C "$SRC_ROOT"
/usr/bin/tar -xjf "$LIBUSB_PATH" -C "$SRC_ROOT"

CH32FUN_SRC="$SRC_ROOT/ch32fun-${CH32FUN_COMMIT}"
MINICHLINK_SRC="$CH32FUN_SRC/minichlink"
LIBUSB_SRC="$SRC_ROOT/libusb-${LIBUSB_VERSION}"
LIBUSB_BUILD="$SRC_ROOT/libusb-build"
[ -f "$MINICHLINK_SRC/Makefile" ] || uiap_die 223 'minichlink Makefile was not found after extraction.'
[ -f "$MINICHLINK_SRC/minichlink.c" ] || uiap_die 223 'minichlink.c was not found after extraction.'
[ -x "$LIBUSB_SRC/configure" ] || uiap_die 224 'Official libusb release configure script was not found.'

mkdir -p "$LIBUSB_BUILD"
uiap_info 'Configuring static libusb for arm64...'
(
    cd "$LIBUSB_BUILD"
    "$LIBUSB_SRC/configure" \
        CC="$CLANG" \
        CFLAGS="-arch arm64 -O2 -isysroot $SDKROOT" \
        LDFLAGS="-arch arm64 -isysroot $SDKROOT" \
        --host=arm-apple-darwin \
        --disable-shared \
        --enable-static \
        --disable-tests-build \
        --disable-examples-build
    "$UIAP_RUNTIME/bin/make"
)
LIBUSB_STATIC="$LIBUSB_BUILD/libusb/.libs/libusb-1.0.a"
[ -f "$LIBUSB_STATIC" ] || uiap_die 225 'Static libusb archive was not generated.'

# minichlink's Makefile probes pkg-config even when explicit libusb paths are supplied.
# A private silent stub prevents a misleading "pkg-config: No such file" message.
STUB_BIN="$BUILD_ROOT/stub-bin"
mkdir -p "$STUB_BIN"
cat > "$STUB_BIN/pkg-config" <<'STUB'
#!/bin/sh
exit 1
STUB
chmod 0755 "$STUB_BIN/pkg-config"

uiap_info 'Building minichlink for macOS arm64...'
(
    cd "$MINICHLINK_SRC"
    PATH="$STUB_BIN:/usr/bin:/bin:/usr/sbin:/sbin" "$UIAP_RUNTIME/bin/make" clean
    PATH="$STUB_BIN:/usr/bin:/bin:/usr/sbin:/sbin" "$UIAP_RUNTIME/bin/make" minichlink \
        ARCH=arm64 \
        CC="$CLANG" \
        LIBUSB_INCS="-I$LIBUSB_SRC/libusb" \
        LIBUSB_LIBS="$LIBUSB_STATIC"
)

CANDIDATE="$MINICHLINK_SRC/minichlink"
[ -x "$CANDIDATE" ] || uiap_die 226 'minichlink executable was not generated.'
MFILE=$(/usr/bin/file "$CANDIDATE" 2>/dev/null || true)
case "$MFILE" in
    *Mach-O*arm64*) : ;;
    *) uiap_die 227 "Generated minichlink is not macOS arm64: $MFILE" ;;
esac

LINKED=$(/usr/bin/otool -L "$CANDIDATE" 2>/dev/null | /usr/bin/tail -n +2 || true)
if printf '%s\n' "$LINKED" | /usr/bin/grep -E '/opt/homebrew/|/usr/local/|/Users/|libusb[^ ]*\.dylib' >/dev/null 2>&1; then
    printf '%s\n' "$LINKED" >&2
    uiap_die 228 'Generated minichlink has a forbidden dynamic-library dependency.'
fi

cp "$CANDIDATE" "$UIAP_RUNTIME/bin/minichlink"
chmod 0755 "$UIAP_RUNTIME/bin/minichlink"

# A browser-downloaded Devkit can propagate com.apple.quarantine to locally built outputs.
# Remove it only from the locally generated minichlink, never recursively from the Devkit.
/usr/bin/xattr -d com.apple.quarantine "$UIAP_RUNTIME/bin/minichlink" 2>/dev/null || true

# Apply a local ad-hoc signature after all binary modifications. This is not Developer ID
# signing or notarization; it prevents a stale linker signature from blocking local testing.
/usr/bin/codesign --force --sign - "$UIAP_RUNTIME/bin/minichlink" >/dev/null 2>&1 \
    || uiap_die 229 'Could not apply an ad-hoc signature to minichlink.'
/usr/bin/codesign --verify --verbose=4 "$UIAP_RUNTIME/bin/minichlink" >/dev/null 2>&1 \
    || uiap_die 230 'Ad-hoc signature verification failed for minichlink.'

if /usr/bin/xattr -p com.apple.quarantine "$UIAP_RUNTIME/bin/minichlink" >/dev/null 2>&1; then
    uiap_die 231 'minichlink still has com.apple.quarantine after local build.'
fi

MINICHLINK_SHA=$(/usr/bin/shasum -a 256 "$UIAP_RUNTIME/bin/minichlink" | /usr/bin/awk '{print $1}')
CLANG_VERSION=$($CLANG --version 2>/dev/null | /usr/bin/head -n 1)
MINICHLINK_VERSION=$(/usr/bin/strings "$UIAP_RUNTIME/bin/minichlink" | /usr/bin/grep -E '^[0-9a-f]{40}$' | /usr/bin/head -n 1 || true)

cat > "$UIAP_RUNTIME/bin/minichlink.build-info" <<META
build_mode=local-source-build
built_at=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
host_arch=$(uname -m)
host_macos=$(/usr/bin/sw_vers -productVersion)
compiler=$CLANG_VERSION
sdk=$SDKROOT
ch32fun_source_commit=$CH32FUN_COMMIT
ch32fun_archive_sha256=$CH32FUN_SHA
minichlink_version_macro=${MINICHLINK_VERSION:-unknown}
libusb_version=$LIBUSB_VERSION
libusb_archive_sha256=$LIBUSB_SHA
libusb_linkage=static
minichlink_sha256=$MINICHLINK_SHA
META
cp "$UIAP_RUNTIME/bin/minichlink.build-info" "$UIAP_DEVKIT_ROOT/.state/minichlink-build-info.txt"

uiap_info 'minichlink local build completed.'
uiap_info "Installed: $UIAP_RUNTIME/bin/minichlink"
uiap_info "SHA-256: $MINICHLINK_SHA"
uiap_info 'Run: doctor'
