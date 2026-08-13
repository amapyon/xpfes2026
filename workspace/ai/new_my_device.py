#!/usr/bin/env python3
"""Create workspace/my/device1 from the participant template."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil


AI_DIR = Path(__file__).resolve().parent
DEFAULT_WORKSPACE = AI_DIR.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=DEFAULT_WORKSPACE, help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workspace = args.workspace.resolve()
    template = workspace / "ai" / "MY_DEVICE_TEMPLATE"
    destination = workspace / "my" / "device1"

    if not template.is_dir():
        print(f"テンプレートがありません: {template}")
        return 1
    if destination.exists():
        print(f"既に存在します。上書きしません: {destination}")
        return 1

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template, destination)
    print(f"created: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
