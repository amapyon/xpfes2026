from __future__ import annotations

import hashlib
from pathlib import Path
from pathlib import PurePosixPath
import subprocess
import shutil
import sys
import tempfile
import unittest
import zipfile

from tools import build_devkit


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools" / "build_devkit.py"


class BuildDevkitTests(unittest.TestCase):
    def build(self, output: Path) -> None:
        subprocess.run(
            [sys.executable, str(BUILDER), "--target", "all", "--version", "0.0.0", "--output", str(output)],
            cwd=ROOT,
            check=True,
        )

    def test_builds_both_deterministic_archives(self) -> None:
        with tempfile.TemporaryDirectory() as first_raw, tempfile.TemporaryDirectory() as second_raw:
            first = Path(first_raw)
            second = Path(second_raw)
            self.build(first)
            self.build(second)
            for architecture in ("win64", "macarm64"):
                name = f"uiap-devkit-{architecture}-0.0.0.zip"
                archive = first / name
                self.assertTrue(archive.is_file())
                self.assertEqual(
                    hashlib.sha256(archive.read_bytes()).digest(),
                    hashlib.sha256((second / name).read_bytes()).digest(),
                )
                with zipfile.ZipFile(archive) as bundle:
                    names = bundle.namelist()
                    self.assertIn(f"uiap-devkit-{architecture}/README.md", names)
                    self.assertIn(f"uiap-devkit-{architecture}/workspace/poc/README.md", names)
                    self.assertIn(f"uiap-devkit-{architecture}/workspace/poc/_template/README.md", names)
                    preflight = f"uiap-devkit-{architecture}/workspace/preflight"
                    for relative in ("README.md", "Makefile", "preflight_hid.c", "usb_config.h", "host/preflight_hid.py"):
                        self.assertIn(f"{preflight}/{relative}", names)
                    launcher = "start-uiap.cmd" if architecture == "win64" else "start-uiap.command"
                    self.assertIn(f"uiap-devkit-{architecture}/{launcher}", names)
                    platform = "win" if architecture == "win64" else "mac"
                    other = "mac" if platform == "win" else "win"
                    common_files = {
                        "00_onboard_led_blink": ("Makefile", "onboard_led_blink.c"),
                        "01_macro_keyboard": ("Makefile", "macro_keyboard.c", "usb_config.h", "host/hidcheck.py"),
                        "02_rotary_cursor_size": ("Makefile", "rotary_cursor_size.c", "usb_config.h"),
                    }
                    for exercise, required in common_files.items():
                        base = f"uiap-devkit-{architecture}/workspace/exercises/{exercise}"
                        for relative in required:
                            self.assertIn(f"{base}/{relative}", names)
                    rotary_host = f"uiap-devkit-{architecture}/workspace/exercises/02_rotary_cursor_size/host"
                    self.assertIn(f"{rotary_host}/{platform}/cursor_size_host.py", names)
                    self.assertFalse(any(name.startswith(f"{rotary_host}/{other}/") for name in names))
                    self.assertFalse(any("\\" in item for item in names))

    def test_checksum_sidecars_match(self) -> None:
        with tempfile.TemporaryDirectory() as output_raw:
            output = Path(output_raw)
            self.build(output)
            for sidecar in output.glob("*.zip.sha256"):
                expected, filename = sidecar.read_text(encoding="ascii").split()
                self.assertEqual(expected, hashlib.sha256((output / filename).read_bytes()).hexdigest())

    def test_poc_platform_directories_are_filtered(self) -> None:
        with tempfile.TemporaryDirectory() as workspace_raw:
            workspace = Path(workspace_raw)
            project = workspace / "poc" / "probe"
            (project / "src").mkdir(parents=True)
            (project / "win").mkdir()
            (project / "mac").mkdir()
            (project / "src" / "common.c").write_text("common\n", encoding="utf-8")
            (project / "win" / "host.py").write_text("win\n", encoding="utf-8")
            (project / "mac" / "host.py").write_text("mac\n", encoding="utf-8")
            (workspace / "deps" / "generated").mkdir(parents=True)
            (workspace / "deps" / "generated" / "tool.bin").write_bytes(b"generated")
            original = build_devkit.WORKSPACE
            try:
                build_devkit.WORKSPACE = workspace
                windows = build_devkit.merged_files("win")
                macos = build_devkit.merged_files("mac")
            finally:
                build_devkit.WORKSPACE = original
            base = PurePosixPath("workspace/poc/probe")
            self.assertIn(base / "src/common.c", windows)
            self.assertIn(base / "win/host.py", windows)
            self.assertNotIn(base / "mac/host.py", windows)
            self.assertIn(base / "src/common.c", macos)
            self.assertIn(base / "mac/host.py", macos)
            self.assertNotIn(base / "win/host.py", macos)
            self.assertNotIn(PurePosixPath("workspace/deps/generated/tool.bin"), windows)
            self.assertNotIn(PurePosixPath("workspace/deps/generated/tool.bin"), macos)


class NewPocTests(unittest.TestCase):
    def test_creates_common_project_from_template(self) -> None:
        with tempfile.TemporaryDirectory() as projects_raw:
            projects = Path(projects_raw)
            shutil.copytree(ROOT / "workspace" / "poc" / "_template", projects / "_template")
            subprocess.run(
                [sys.executable, str(ROOT / "tools" / "new_poc.py"), "sample_probe", "--poc-dir", str(projects)],
                cwd=ROOT,
                check=True,
            )
            project = projects / "sample_probe"
            self.assertIn("sample_probe", (project / "README.md").read_text(encoding="utf-8"))
            self.assertTrue((project / "src" / "poc.c").is_file())
            self.assertFalse((project / "win").exists())
            self.assertFalse((project / "mac").exists())


class UnifiedRepositoryTests(unittest.TestCase):
    def test_macos_commands_are_git_executable(self) -> None:
        paths = ["start-uiap.command"]
        paths.extend(path.relative_to(ROOT).as_posix() for path in (ROOT / "scripts").rglob("*.sh"))
        paths.extend(path.relative_to(ROOT).as_posix() for path in (ROOT / "scripts" / "bin").iterdir() if path.is_file())
        result = subprocess.run(
            ["git", "ls-files", "--stage", "--", *paths],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        modes = {line.split(maxsplit=3)[3]: line.split(maxsplit=1)[0] for line in result.stdout.splitlines()}
        for path in paths:
            self.assertEqual("100755", modes.get(path), path)

    def test_launchers_select_platform_runtime(self) -> None:
        windows = (ROOT / "start-uiap.cmd").read_text(encoding="utf-8-sig")
        macos = (ROOT / "scripts" / "env.sh").read_text(encoding="utf-8")
        self.assertIn('UIAP_PLATFORM=win', windows)
        self.assertIn(r'runtime\win', windows)
        self.assertIn('UIAP_PLATFORM=mac', macos)
        self.assertIn('runtime/mac', macos)

    def test_required_exercises_have_expected_source_layout(self) -> None:
        requirements = {
            "00_onboard_led_blink": ("onboard_led_blink.c",),
            "01_macro_keyboard": ("macro_keyboard.c", "usb_config.h", "host/hidcheck.py"),
            "02_rotary_cursor_size": ("rotary_cursor_size.c", "usb_config.h"),
        }
        for exercise, files in requirements.items():
            root = ROOT / "workspace" / "exercises" / exercise
            self.assertTrue((root / "Makefile").is_file())
            for relative in files:
                self.assertTrue((root / relative).is_file(), f"{exercise}/{relative}")
            self.assertFalse((root / "win").exists())
            self.assertFalse((root / "mac").exists())

        rotary_host = ROOT / "workspace" / "exercises" / "02_rotary_cursor_size" / "host"
        for platform in ("win", "mac"):
            self.assertTrue((rotary_host / platform / "cursor_size_host.py").is_file())

    def test_macos_setup_builds_write_tool(self) -> None:
        setup = (ROOT / "scripts" / "setup.sh").read_text(encoding="utf-8")
        self.assertIn('scripts/build-minichlink.sh', setup)
        self.assertIn('UIAP_RUNTIME/bin/minichlink', setup)


if __name__ == "__main__":
    unittest.main()
