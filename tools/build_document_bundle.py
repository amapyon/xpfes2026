#!/usr/bin/env python3
"""Build a compact ZIP of source documents for workshop-slide generation."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path, PurePosixPath
import stat
import zipfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "dist" / "workshop-slide-docs.zip"
ZIP_TIME = (2026, 1, 1, 0, 0, 0)

SLIDE_FILES = (
    "README.md",
    "docs/README.md",
    "docs/DEVELOPMENT_WORKFLOW.md",
    "docs/project/00_PROJECT_OVERVIEW.md",
    "docs/project/10_DEVKIT_STRUCTURE.md",
    "docs/project/30_HARDWARE_RULES.md",
    "docs/project/40_WORKSHOP_GUIDE_RULES.md",
    "docs/project/60_TROUBLESHOOTING.md",
    "docs/project/70_VALIDATION_RESULTS.md",
    "workspace/README.md",
    "workspace/preflight/README.md",
    "workspace/exercises/README.md",
    "workspace/exercises/00_onboard_led_blink/README.md",
    "workspace/exercises/01_macro_keyboard/README.md",
    "workspace/exercises/02_rotary_cursor_size/README.md",
    "workspace/exercises/02_rotary_cursor_size/host/README.md",
    "workspace/exercises/03_vibration_motor_console/README.md",
    "workspace/exercises/03_vibration_motor_console/host/README.md",
    "workspace/exercises/04_rotary_cursor_haptic/README.md",
    "workspace/exercises/04_rotary_cursor_haptic/host/README.md",
    "workspace/ai/README.md",
    "workspace/ai/BOARD_FOR_AI.md",
    "workspace/ai/PROGRAM_GENERATION_PROMPT.md",
    "workspace/ai/WEB_UPLOAD_CHECKLIST.md",
    "workspace/ai/MY_DEVICE_ZIP_CHECKLIST.md",
    "workspace/ai/BUILD_ERROR_TEMPLATE.txt",
    "workspace/ai/MY_DEVICE_TEMPLATE/README.md",
    "workspace/ai/MY_DEVICE_TEMPLATE/REQUIREMENTS.md",
    "workspace/ai/MY_DEVICE_TEMPLATE/WIRING.md",
    "workspace/parts/PARTS_FOR_AI.md",
    "workspace/my/README.md",
)

FULL_EXTRA_FILES = (
    "docs/project/15_CH32FUN_SUBSET_RULES.md",
    "docs/project/20_BUILD_RULES.md",
    "docs/project/50_RELEASE_CHECKLIST.md",
    "docs/project/90_DECISIONS.md",
)


def setup_documents() -> tuple[str, ...]:
    return tuple(
        path.relative_to(ROOT).as_posix()
        for path in sorted((ROOT / "docs" / "setup").rglob("*.md"))
    )


def selected_files(profile: str) -> tuple[str, ...]:
    selected = set(SLIDE_FILES)
    selected.update(setup_documents())
    if profile == "full":
        selected.update(FULL_EXTRA_FILES)
    return tuple(sorted(selected))


def introduction(profile: str, files: tuple[str, ...]) -> str:
    exclusions = [
        "docs/project/99_FULL_PROJECT_GUIDE.md（分割文書を結合した重複版）",
        "workspace/poc/（主催者の検証用で、研修の正式手順ではない）",
        "プログラム、ビルド生成物、ランタイム",
    ]
    if profile == "slides":
        exclusions.insert(1, "リリース作業・内部ビルド規約・判断履歴の詳細（--profile fullで追加可能）")

    file_list = "\n".join(f"- `{name}`" for name in files)
    exclusion_list = "\n".join(f"- {item}" for item in exclusions)
    return f"""# 研修スライド作成AI向けドキュメント

このZIPは、UIAPduinoワークショップの研修スライドを別の生成AIで作成するための入力資料です。

## 読み方

1. `docs/project/00_PROJECT_OVERVIEW.md`で目的と確定事項を把握する
2. `docs/project/40_WORKSHOP_GUIDE_RULES.md`をスライドの表現・構成規則として扱う
3. `workspace/exercises/`のREADMEを当日の演習手順の正本とする
4. 自由制作は`workspace/ai/README.md`、基板は`BOARD_FOR_AI.md`、部品は`PARTS_FOR_AI.md`を正本とする
5. `70_VALIDATION_RESULTS.md`にない実機結果を「確認済み」と表現しない

文書間で差がある場合は、個別の正本文書を統合版や概要より優先してください。未確認事項を推測で確定しないでください。

## このZIPのプロファイル

- プロファイル: `{profile}`
- 収録ファイル数: {len(files)}
- 生成コマンド: `python tools/build_document_bundle.py`
- 詳細も含める場合: `python tools/build_document_bundle.py --profile full`

## 意図的に含めないもの

{exclusion_list}

## 収録ファイル

{file_list}
"""


def write_entry(bundle: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(PurePosixPath(name).as_posix(), ZIP_TIME)
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    bundle.writestr(info, data)


def build(output: Path, profile: str) -> tuple[Path, str, tuple[str, ...]]:
    files = selected_files(profile)
    missing = [name for name in files if not (ROOT / name).is_file()]
    if missing:
        raise FileNotFoundError("収録対象がありません: " + ", ".join(missing))

    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        write_entry(bundle, "00_READ_ME_FIRST.md", introduction(profile, files).encode("utf-8"))
        for name in files:
            write_entry(bundle, name, (ROOT / name).read_bytes())

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + ".sha256").write_text(
        f"{digest}  {output.name}\n", encoding="ascii", newline="\n"
    )
    return output, digest, files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("slides", "full"), default="slides")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        output, digest, files = build(args.output, args.profile)
    except (OSError, FileNotFoundError) as exc:
        print(f"document bundle error: {exc}")
        return 1
    print(f"created: {output}")
    print(f"profile: {args.profile}, files: {len(files)}, sha256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
