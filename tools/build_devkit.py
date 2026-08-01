#!/usr/bin/env python3
"""Build deterministic Windows and macOS participant-kit ZIP files."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path, PurePosixPath
import stat
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "workspace"
TARGETS = {
    "win": "win64",
    "mac": "macarm64",
}
FORBIDDEN_SUFFIXES = {".elf", ".bin", ".hex", ".lst", ".map", ".log", ".pyc"}
FORBIDDEN_PARTS = {"__pycache__", ".state"}
ZIP_TIME = (2026, 1, 1, 0, 0, 0)


class BuildError(RuntimeError):
    pass


def relative_files(source: Path) -> dict[PurePosixPath, Path]:
    result: dict[PurePosixPath, Path] = {}
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise BuildError(f"シンボリックリンクは配布元に使用できません: {source.name}/{path.relative_to(source)}")
        if not path.is_file() or path.name == ".gitkeep":
            continue
        relative = PurePosixPath(path.relative_to(source).as_posix())
        if FORBIDDEN_PARTS.intersection(relative.parts):
            continue
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            raise BuildError(f"配布禁止の生成物が含まれています: {source.name}/{relative}")
        result[relative] = path
    return result


def add_files(
    destination: dict[PurePosixPath, Path],
    source: Path,
    prefix: PurePosixPath = PurePosixPath(),
    include: object | None = None,
) -> None:
    for relative, path in relative_files(source).items():
        if include is not None and not include(relative):  # type: ignore[operator]
            continue
        packaged = prefix / relative
        if packaged in destination:
            raise BuildError(f"配布パスが重複しています: {packaged}")
        destination[packaged] = path


def workspace_file_for_target(relative: PurePosixPath, target: str) -> bool:
    parts = relative.parts
    if len(parts) >= 3 and parts[0] in {"exercises", "poc"}:
        platform_part = parts[2]
        if platform_part in {"win", "mac"}:
            return platform_part == target
    return True


def script_file_for_target(relative: PurePosixPath, target: str) -> bool:
    if relative.parts[0] == "python":
        return True
    if target == "win":
        return relative.parts[0] == "cmd" or relative.suffix == ".ps1"
    return (
        relative.parts[0] in {"bin", "lib", "zsh"}
        or relative.suffix == ".sh"
    )


def merged_files(target: str) -> dict[PurePosixPath, Path]:
    files: dict[PurePosixPath, Path] = {
        PurePosixPath("README.md"): ROOT / "README.md",
        PurePosixPath("VERSION"): ROOT / "VERSION",
    }
    launcher = "start-uiap.cmd" if target == "win" else "start-uiap.command"
    files[PurePosixPath(launcher)] = ROOT / launcher
    add_files(files, WORKSPACE, PurePosixPath("workspace"), lambda path: workspace_file_for_target(path, target))
    add_files(files, ROOT / "scripts", PurePosixPath("scripts"), lambda path: script_file_for_target(path, target))
    add_files(files, ROOT / "config" / target, PurePosixPath("config") / target)
    add_files(files, ROOT / "docs" / "setup" / target, PurePosixPath("docs"))
    add_files(files, ROOT / "licenses" / target, PurePosixPath("licenses"))
    add_files(files, ROOT / "firmware", PurePosixPath("firmware"))
    return files


def executable(relative: PurePosixPath) -> bool:
    return (
        relative.suffix in {".sh", ".command"}
        or "scripts/bin" in relative.as_posix()
    )


def build_zip(target: str, version: str, output: Path) -> tuple[Path, str]:
    architecture = TARGETS[target]
    root_name = f"uiap-devkit-{architecture}"
    archive = output / f"{root_name}-{version}.zip"
    files = merged_files(target)
    output.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for relative, source in sorted(files.items()):
            name = PurePosixPath(root_name) / relative
            info = zipfile.ZipInfo(name.as_posix(), ZIP_TIME)
            info.create_system = 3
            mode = 0o755 if executable(relative) else 0o644
            info.external_attr = (stat.S_IFREG | mode) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            bundle.writestr(info, source.read_bytes())

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    sidecar = archive.with_suffix(archive.suffix + ".sha256")
    sidecar.write_text(f"{digest}  {archive.name}\n", encoding="ascii", newline="\n")
    return archive, digest


def clean_known_outputs(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for pattern in ("uiap-devkit-win64-*.zip*", "uiap-devkit-macarm64-*.zip*", "SHA256SUMS"):
        for path in output.glob(pattern):
            if path.is_file():
                path.unlink()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=("all", *TARGETS), default="all")
    parser.add_argument("--version", help="ZIP名に使用する版番号。省略時はルートVERSION")
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    version = args.version
    if version is None:
        for line in (ROOT / "VERSION").read_text(encoding="utf-8").splitlines():
            if line.startswith("Version:"):
                version = line.split(":", 1)[1].strip()
                break
    version = (version or "").strip()
    if not version or any(character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-" for character in version):
        print("版番号には英数字、ピリオド、ハイフン、アンダースコアだけを使用してください。", file=sys.stderr)
        return 2
    output = args.output.resolve()
    clean_known_outputs(output)
    targets = TARGETS if args.target == "all" else (args.target,)
    checksums: list[tuple[str, str]] = []
    try:
        for target in targets:
            archive, digest = build_zip(target, version, output)
            checksums.append((archive.name, digest))
            print(f"created: {archive}")
    except BuildError as exc:
        print(f"build error: {exc}", file=sys.stderr)
        return 1
    (output / "SHA256SUMS").write_text(
        "".join(f"{digest}  {name}\n" for name, digest in sorted(checksums)),
        encoding="ascii",
        newline="\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
