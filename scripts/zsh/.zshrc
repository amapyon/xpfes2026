# UIAP Devkit専用zsh初期化。ユーザーの~/.zshrcは読み込まない。

setup() {
    /bin/sh "$UIAP_DEVKIT_ROOT/scripts/setup.sh" "$@"
}

doctor() {
    /bin/sh "$UIAP_DEVKIT_ROOT/scripts/doctor.sh" "$@"
}

versions() {
    /bin/sh "$UIAP_DEVKIT_ROOT/scripts/versions.sh" "$@"
}

report() {
    /bin/sh "$UIAP_DEVKIT_ROOT/scripts/report.sh" "$@"
}

make() {
    /bin/sh "$UIAP_RUNTIME/bin/make" "$@"
}

export PS1='uiap:%1~ %# '
