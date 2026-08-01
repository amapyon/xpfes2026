#!/usr/bin/env python3
import ast
from pathlib import Path
import sys

if len(sys.argv) != 2:
    print("usage: syntax_probe.py <python-file>", file=sys.stderr)
    raise SystemExit(64)
path = Path(sys.argv[1])
try:
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
except Exception as exc:
    print(f"[UIAP-E208] Python syntax check failed: {exc}", file=sys.stderr)
    raise SystemExit(208)
print(f"Python syntax: PASS {path.name}")
