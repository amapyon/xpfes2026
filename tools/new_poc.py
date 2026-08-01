#!/usr/bin/env python3
"""Create a PoC project from workspace/poc/_template."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POC_DIR = ROOT / "workspace" / "poc"
VALID_NAME = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="例: rotary_cursor_probe")
    parser.add_argument("--poc-dir", type=Path, default=DEFAULT_POC_DIR, help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not VALID_NAME.fullmatch(args.name):
        print("プロジェクト名には小文字英数字、ハイフン、アンダースコアを使用してください。", file=sys.stderr)
        return 2

    poc_dir = args.poc_dir.resolve()
    template = poc_dir / "_template"
    destination = poc_dir / args.name
    if not template.is_dir():
        print(f"テンプレートがありません: {template}", file=sys.stderr)
        return 1
    if destination.exists():
        print(f"既に存在します: {destination}", file=sys.stderr)
        return 1

    shutil.copytree(template, destination)
    for path in destination.rglob("*"):
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        path.write_text(content.replace("{{PROJECT_NAME}}", args.name), encoding="utf-8", newline="\n")
    print(f"created: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
