#!/usr/bin/env python3
"""Create safe, self-contained input packs for Web-based generative AI."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
import zipfile


AI_DIR = Path(__file__).resolve().parent
DEFAULT_WORKSPACE = AI_DIR.parent
OUTPUT_MARKER = ".uiap_web_handoff"
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_TOTAL_BYTES = 20 * 1024 * 1024

CORE_FILES = (
    "ai/PROGRAM_GENERATION_PROMPT.md",
    "ai/BOARD_FOR_AI.md",
    "ai/WEB_UPLOAD_CHECKLIST.md",
    "ai/MY_DEVICE_ZIP_CHECKLIST.md",
    "parts/PARTS_FOR_AI.md",
    "my/device1/REQUIREMENTS.md",
    "my/device1/WIRING.md",
    "ai/MY_DEVICE_TEMPLATE/README.md",
    "ai/MY_DEVICE_TEMPLATE/REQUIREMENTS.md",
    "ai/MY_DEVICE_TEMPLATE/WIRING.md",
    "ai/MY_DEVICE_TEMPLATE/Makefile",
    "ai/MY_DEVICE_TEMPLATE/device1.c",
    "ai/MY_DEVICE_TEMPLATE/funconfig.h",
)

ALLOWED_REFERENCE_ROOTS = ("exercises", "poc")
ALLOWED_SUFFIXES = {
    ".c",
    ".h",
    ".s",
    ".py",
    ".md",
    ".txt",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".config",
}
ALLOWED_NAMES = {"Makefile", ".gitignore"}
FORBIDDEN_SUFFIXES = {".elf", ".bin", ".hex", ".map", ".lst", ".o", ".log", ".zip"}
FORBIDDEN_NAMES = {
    ".env",
    "id_rsa",
    "id_ed25519",
    "credentials.json",
    "secrets.json",
}
SKIPPED_DIRECTORIES = {".git", "__pycache__", ".cache", "deps", "runtime"}


class HandoffError(RuntimeError):
    """A user-correctable handoff preparation error."""


@dataclass(frozen=True)
class SourceFile:
    source: Path
    relative: PurePosixPath
    size: int
    sha256: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Web版生成AIへ渡すフォルダー、Markdown、ZIPを安全に作成します。"
    )
    parser.add_argument(
        "--reference",
        action="append",
        default=[],
        metavar="PATH",
        help=(
            "追加する演習またはPoC。例: exercises/01_macro_keyboard。"
            "複数回指定できます。通常はREQUIREMENTS.mdから自動検出されます。"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="出力先。既定値はworkspace/my/WEB_HANDOFF_device1です。",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="このツールが以前作成した出力先だけを置き換えます。",
    )
    parser.add_argument("--workspace", type=Path, default=DEFAULT_WORKSPACE, help=argparse.SUPPRESS)
    return parser.parse_args()


def path_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def read_utf8(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise HandoffError(f"UTF-8のテキストとして読めません: {path}") from exc


def validate_source(path: Path, workspace: Path) -> SourceFile:
    if path.is_symlink():
        raise HandoffError(f"シンボリックリンクは添付しません: {path}")
    if not path.is_file():
        raise HandoffError(f"必要なファイルがありません: {path}")
    resolved = path.resolve()
    if not path_within(resolved, workspace):
        raise HandoffError(f"workspace外のファイルは添付できません: {path}")
    if path.name in FORBIDDEN_NAMES or path.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}:
        raise HandoffError(f"秘密情報の可能性があるファイルは添付できません: {path}")
    if path.suffix.lower() in FORBIDDEN_SUFFIXES:
        raise HandoffError(f"ビルド生成物またはアーカイブは添付できません: {path}")
    if path.name not in ALLOWED_NAMES and path.suffix.lower() not in ALLOWED_SUFFIXES:
        raise HandoffError(f"許可されていない形式です: {path}")
    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        raise HandoffError(f"1ファイルの上限2MBを超えています: {path}")
    data = path.read_bytes()
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HandoffError(f"UTF-8のテキストではありません: {path}") from exc
    relative = PurePosixPath("workspace") / PurePosixPath(resolved.relative_to(workspace).as_posix())
    return SourceFile(resolved, relative, size, hashlib.sha256(data).hexdigest())


def reference_catalog(workspace: Path) -> dict[str, Path]:
    catalog: dict[str, Path] = {}
    duplicates: set[str] = set()
    for root_name in ALLOWED_REFERENCE_ROOTS:
        root = workspace / root_name
        if not root.is_dir():
            continue
        for child in root.iterdir():
            if not child.is_dir() or child.name.startswith("_"):
                continue
            if child.name in catalog:
                duplicates.add(child.name)
            else:
                catalog[child.name] = child
    for duplicate in duplicates:
        catalog.pop(duplicate, None)
    return catalog


def normalize_reference(value: str, workspace: Path) -> Path:
    normalized = value.strip().replace("\\", "/").strip("/")
    if normalized.startswith("workspace/"):
        normalized = normalized[len("workspace/") :]
    parts = PurePosixPath(normalized).parts
    if len(parts) != 2 or parts[0] not in ALLOWED_REFERENCE_ROOTS or parts[1].startswith("_"):
        raise HandoffError(
            "参照先はexercises/<名前>またはpoc/<名前>で指定してください: " + value
        )
    result = (workspace / parts[0] / parts[1]).resolve()
    allowed_root = (workspace / parts[0]).resolve()
    if not path_within(result, allowed_root) or not result.is_dir():
        raise HandoffError(f"参照先がありません: workspace/{normalized}")
    return result


def discover_references(workspace: Path, explicit: list[str]) -> list[Path]:
    requirements = read_utf8(workspace / "my" / "device1" / "REQUIREMENTS.md")
    wiring = read_utf8(workspace / "my" / "device1" / "WIRING.md")
    combined = requirements + "\n" + wiring
    found: set[Path] = set()

    path_pattern = re.compile(r"workspace/(exercises|poc)/([A-Za-z0-9_.-]+)")
    for root_name, project_name in path_pattern.findall(combined):
        found.add(normalize_reference(f"{root_name}/{project_name}", workspace))

    catalog = reference_catalog(workspace)
    for name, path in catalog.items():
        if re.search(rf"(?<![A-Za-z0-9_.-]){re.escape(name)}(?![A-Za-z0-9_.-])", combined):
            found.add(path.resolve())

    for value in explicit:
        found.add(normalize_reference(value, workspace))
    return sorted(found, key=lambda path: path.relative_to(workspace).as_posix())


def reference_files(reference: Path, workspace: Path, excluded: list[PurePosixPath]) -> list[SourceFile]:
    result: list[SourceFile] = []
    for path in sorted(reference.rglob("*"), key=lambda item: item.as_posix()):
        relative_parts = path.relative_to(reference).parts
        if any(part in SKIPPED_DIRECTORIES for part in relative_parts):
            continue
        if path.is_dir():
            continue
        if path.is_symlink():
            raise HandoffError(f"参照実装内にシンボリックリンクがあります: {path}")
        if path.name in FORBIDDEN_NAMES or path.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}:
            raise HandoffError(f"参照実装に秘密情報の可能性があるファイルがあります: {path}")
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            excluded.append(PurePosixPath("workspace") / PurePosixPath(path.relative_to(workspace).as_posix()))
            continue
        if path.name not in ALLOWED_NAMES and path.suffix.lower() not in ALLOWED_SUFFIXES:
            continue
        result.append(validate_source(path, workspace))
    if not result:
        raise HandoffError(f"参照実装に添付可能なファイルがありません: {reference}")
    return result


def collect_sources(
    workspace: Path, explicit_references: list[str]
) -> tuple[list[SourceFile], list[Path], list[PurePosixPath]]:
    sources = [validate_source(workspace / relative, workspace) for relative in CORE_FILES]
    references = discover_references(workspace, explicit_references)
    excluded: list[PurePosixPath] = []
    sources.extend(reference_files(workspace / "my" / "device1", workspace, excluded))
    for reference in references:
        sources.extend(reference_files(reference, workspace, excluded))

    unique: dict[PurePosixPath, SourceFile] = {}
    for source in sources:
        unique[source.relative] = source
    ordered = [unique[key] for key in sorted(unique, key=str)]
    total = sum(source.size for source in ordered)
    if total > MAX_TOTAL_BYTES:
        raise HandoffError(f"添付資料の合計が上限20MBを超えています: {total} bytes")
    return ordered, references, sorted(set(excluded), key=str)


def manifest_text(
    sources: list[SourceFile],
    references: list[Path],
    excluded: list[PurePosixPath],
    workspace: Path,
) -> str:
    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    reference_names = [f"workspace/{path.relative_to(workspace).as_posix()}" for path in references]
    reference_section = "\n".join(f"- `{name}`" for name in reference_names) or "- なし"
    excluded_section = "\n".join(f"- `{path}`" for path in excluded) or "- なし"
    rows = "\n".join(
        f"| `{source.relative}` | {source.size} | `{source.sha256}` |" for source in sources
    )
    return f"""# AI Web受け渡しマニフェスト

- 生成日時（UTC）: {generated}
- 対象: `workspace/my/device1`
- ファイル数: {len(sources)}
- 合計サイズ: {sum(source.size for source in sources)} bytes

## AIへの重要事項

- このパック内の資料だけを根拠として使用してください。
- `workspace/my/device1/REQUIREMENTS.md`と`workspace/my/device1/WIRING.md`が今回の正本です。
- `workspace/ai/MY_DEVICE_TEMPLATE/REQUIREMENTS.md`と`WIRING.md`は書式の参考であり、今回の正本ではありません。
- マニフェストにないローカルファイルを読めたと仮定してはいけません。
- 不足、矛盾、読めないファイルがある場合はプログラム生成を停止してください。

## 選択された参考実装

{reference_section}

## 自動的に除外したビルド生成物

{excluded_section}

## 収録ファイル

| 元の相対パス | サイズ | SHA-256 |
|---|---:|---|
{rows}
"""


def combined_markdown(manifest: str, sources: list[SourceFile]) -> str:
    sections = [manifest.rstrip(), "\n# 収録ファイル全文"]
    for source in sources:
        text = read_utf8(source.source)
        sections.append(
            f"\n===== BEGIN FILE: {source.relative} =====\n{text.rstrip()}\n"
            f"===== END FILE: {source.relative} ====="
        )
    return "\n\n".join(sections) + "\n"


def write_zip(path: Path, upload_root: Path) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source in sorted(upload_root.rglob("*"), key=lambda item: item.as_posix()):
            if not source.is_file():
                continue
            relative = source.relative_to(upload_root).as_posix()
            info = zipfile.ZipInfo(f"AI_HANDOFF/{relative}", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes())


def prepare_output(output: Path, force: bool) -> None:
    if not output.exists():
        return
    marker = output / OUTPUT_MARKER
    if not force:
        raise HandoffError(f"出力先が既にあります。確認後、--forceで更新してください: {output}")
    if not marker.is_file() or marker.read_text(encoding="ascii").strip() != "uiap-web-handoff-v1":
        raise HandoffError(f"このツールが作成したと確認できないため削除しません: {output}")
    shutil.rmtree(output)


def build(workspace: Path, output: Path, explicit_references: list[str], force: bool) -> tuple[int, int, int]:
    workspace = workspace.resolve()
    output = output.resolve()
    if not workspace.is_dir():
        raise HandoffError(f"workspaceがありません: {workspace}")
    participant_root = (workspace / "my").resolve()
    device_root = (participant_root / "device1").resolve()
    if output == participant_root or not path_within(output, participant_root) or path_within(output, device_root):
        raise HandoffError("出力先はworkspace/my内かつworkspace/my/device1外にしてください。")
    prepare_output(output, force)
    sources, references, excluded = collect_sources(workspace, explicit_references)
    manifest = manifest_text(sources, references, excluded, workspace)

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="uiap-handoff-", dir=output.parent) as temporary_raw:
        temporary = Path(temporary_raw) / output.name
        upload = temporary / "UPLOAD_THIS_FOLDER"
        upload.mkdir(parents=True)
        (temporary / OUTPUT_MARKER).write_text("uiap-web-handoff-v1\n", encoding="ascii")
        (upload / "AI_HANDOFF_MANIFEST.md").write_text(manifest, encoding="utf-8", newline="\n")
        for source in sources:
            destination = upload / "sources" / Path(*source.relative.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source.source, destination)
        (temporary / "AI_HANDOFF.md").write_text(
            combined_markdown(manifest, sources), encoding="utf-8", newline="\n"
        )
        write_zip(temporary / "AI_HANDOFF.zip", upload)
        os.replace(temporary, output)
    return len(sources), sum(source.size for source in sources), len(excluded)


def main() -> int:
    args = parse_args()
    workspace = args.workspace.resolve()
    output = (args.output or (workspace / "my" / "WEB_HANDOFF_device1")).resolve()
    try:
        count, total, excluded_count = build(workspace, output, args.reference, args.force)
    except HandoffError as exc:
        print(f"作成できません: {exc}")
        return 1

    print(f"作成しました: {output}")
    print(f"収録: {count}ファイル、{total} bytes")
    print(f"除外したビルド生成物: {excluded_count}ファイル")
    print(f"Gemini: {output / 'UPLOAD_THIS_FOLDER'}")
    print(f"Copilot Cowork: {output / 'AI_HANDOFF.zip'}")
    print(f"その他のWeb版生成AI: {output / 'AI_HANDOFF.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
