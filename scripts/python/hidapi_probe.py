#!/usr/bin/env python3
from __future__ import annotations
import platform
import sys
try:
    import hid
except Exception as exc:
    print(f"[UIAP-E207] Bundled Python could not import hidapi: {exc}", file=sys.stderr)
    raise SystemExit(207)
print(f"Python: {platform.python_version()}")
print(f"Architecture: {platform.machine()}")
print(f"hidapi module: {getattr(hid, '__file__', 'unknown')}")
print("hidapi import: PASS")
