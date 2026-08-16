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

from tools import build_devkit, build_document_bundle


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools" / "build_devkit.py"


class BuildDevkitTests(unittest.TestCase):
    VERSION = build_devkit.read_package_version()

    def build(self, output: Path) -> None:
        subprocess.run(
            [sys.executable, str(BUILDER), "--target", "all", "--output", str(output)],
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
                name = f"uiap-devkit-{architecture}-{self.VERSION}.zip"
                archive = first / name
                self.assertTrue(archive.is_file())
                self.assertEqual(
                    hashlib.sha256(archive.read_bytes()).digest(),
                    hashlib.sha256((second / name).read_bytes()).digest(),
                )
                with zipfile.ZipFile(archive) as bundle:
                    names = bundle.namelist()
                    self.assertFalse(
                        any(PurePosixPath(name).suffix.lower() in build_devkit.FORBIDDEN_SUFFIXES for name in names)
                    )
                    self.assertIn(f"uiap-devkit-{architecture}/README.md", names)
                    self.assertIn(f"uiap-devkit-{architecture}/workspace/poc/README.md", names)
                    self.assertIn(f"uiap-devkit-{architecture}/workspace/my/README.md", names)
                    self.assertNotIn(f"uiap-devkit-{architecture}/workspace/poc/_poc_template/README.md", names)
                    self.assertIn(f"uiap-devkit-{architecture}/workspace/ai/README.md", names)
                    ai_files = (
                        "BOARD_FOR_AI.md",
                        "PROGRAM_GENERATION_PROMPT.md",
                        "WEB_UPLOAD_CHECKLIST.md",
                        "MY_DEVICE_ZIP_CHECKLIST.md",
                        "BUILD_ERROR_TEMPLATE.txt",
                        "new_my_device.py",
                        "prepare_web_handoff.py",
                        "MY_DEVICE_TEMPLATE/README.md",
                        "MY_DEVICE_TEMPLATE/REQUIREMENTS.md",
                        "MY_DEVICE_TEMPLATE/WIRING.md",
                        "MY_DEVICE_TEMPLATE/Makefile",
                        "MY_DEVICE_TEMPLATE/device1.c",
                        "MY_DEVICE_TEMPLATE/funconfig.h",
                        "MY_DEVICE_TEMPLATE/.gitignore",
                    )
                    ai_base = f"uiap-devkit-{architecture}/workspace/ai"
                    for relative in ai_files:
                        self.assertIn(f"{ai_base}/{relative}", names)
                    parts_catalog = f"uiap-devkit-{architecture}/workspace/parts/PARTS_FOR_AI.md"
                    self.assertIn(parts_catalog, names)
                    parts_text = bundle.read(parts_catalog).decode("utf-8")
                    for part_number in range(1, 10):
                        self.assertIn(f"## PART-{part_number:02d}", parts_text)
                    poc_files = {
                        "vibration_motor_hid": (
                            "Makefile",
                            "src/vibration_motor_hid.c",
                            "src/usb_config.h",
                            "host/motorctl.py",
                        ),
                        "ws2812b8_hid_poc": (
                            "Makefile",
                            "ws2812b8_hid.c",
                            "usb_config.h",
                            "host/ws2812b8_host.py",
                        ),
                    }
                    for poc, required in poc_files.items():
                        base = f"uiap-devkit-{architecture}/workspace/poc/{poc}"
                        for relative in required:
                            self.assertIn(f"{base}/{relative}", names)
                    preflight = f"uiap-devkit-{architecture}/workspace/preflight"
                    for relative in ("README.md", "Makefile", "preflight_hid.c", "usb_config.h", "host/preflight_hid.py"):
                        self.assertIn(f"{preflight}/{relative}", names)
                    launcher = "start-uiap.cmd" if architecture == "win64" else "start-uiap.command"
                    self.assertIn(f"uiap-devkit-{architecture}/{launcher}", names)
                    common_files = {
                        "00_onboard_led_blink": ("Makefile", "onboard_led_blink.c"),
                        "01_macro_keyboard": ("Makefile", "macro_keyboard.c", "usb_config.h", "host/hidcheck.py"),
                        "02_rotary_cursor_size": ("Makefile", "rotary_cursor_size.c", "usb_config.h"),
                        "03_vibration_motor_console": ("Makefile", "vibration_motor_console.c", "usb_config.h", "haptic_pattern.h", "haptic_pattern_protocol.h", "host/motorctl.py"),
                        "04_rotary_cursor_haptic": ("Makefile", "rotary_cursor_size.c", "usb_config.h", "haptic_pattern.h", "haptic_pattern_protocol.h"),
                    }
                    for exercise, required in common_files.items():
                        base = f"uiap-devkit-{architecture}/workspace/exercises/{exercise}"
                        for relative in required:
                            self.assertIn(f"{base}/{relative}", names)
                    unified_host = (
                        f"uiap-devkit-{architecture}/workspace/exercises/"
                        "02_rotary_cursor_size/host/cursor_size_host.py"
                    )
                    self.assertIn(unified_host, names)
                    rotary_host = (
                        f"uiap-devkit-{architecture}/workspace/exercises/"
                        "02_rotary_cursor_size/host"
                    )
                    self.assertFalse(any(name.startswith(f"{rotary_host}/win/") for name in names))
                    self.assertFalse(any(name.startswith(f"{rotary_host}/mac/") for name in names))
                    haptic_host = (
                        f"uiap-devkit-{architecture}/workspace/exercises/"
                        "04_rotary_cursor_haptic/host"
                    )
                    self.assertIn(f"{haptic_host}/cursor_size_host.py", names)
                    self.assertFalse(any(name.startswith(f"{haptic_host}/win/") for name in names))
                    self.assertFalse(any(name.startswith(f"{haptic_host}/mac/") for name in names))
                    self.assertFalse(any("\\" in item for item in names))

    def test_distribution_version_metadata_matches(self) -> None:
        build_devkit.validate_version_metadata(("win", "mac"), self.VERSION)

    def test_rejects_mismatched_lock_version(self) -> None:
        with tempfile.TemporaryDirectory() as root_raw:
            root = Path(root_raw)
            lock = root / "config" / "win" / "bootstrap.lock.json"
            lock.parent.mkdir(parents=True)
            lock.write_text('{"devkit_version":"0.1.0-dev"}\n', encoding="utf-8")
            with self.assertRaises(build_devkit.BuildError):
                build_devkit.validate_version_metadata(("win",), "0.1.1", root)

    def test_rejects_filename_version_override(self) -> None:
        with tempfile.TemporaryDirectory() as output_raw:
            result = subprocess.run(
                [
                    sys.executable,
                    str(BUILDER),
                    "--target",
                    "win",
                    "--version",
                    "9.9.9",
                    "--output",
                    output_raw,
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(2, result.returncode)
            self.assertIn("VERSION=", result.stderr)
            self.assertFalse(list(Path(output_raw).glob("*.zip")))

    def test_checksum_sidecars_match(self) -> None:
        with tempfile.TemporaryDirectory() as output_raw:
            output = Path(output_raw)
            self.build(output)
            for sidecar in output.glob("*.zip.sha256"):
                expected, filename = sidecar.read_text(encoding="ascii").split()
                self.assertEqual(expected, hashlib.sha256((output / filename).read_bytes()).hexdigest())

    def test_forbidden_artifacts_are_excluded_without_modifying_sources(self) -> None:
        with tempfile.TemporaryDirectory() as clean_raw, tempfile.TemporaryDirectory() as dirty_raw:
            clean = Path(clean_raw)
            dirty = Path(dirty_raw)
            (clean / "src").mkdir()
            (dirty / "src").mkdir()
            (clean / "src" / "keep.c").write_text("keep\n", encoding="utf-8")
            (dirty / "src" / "keep.c").write_text("keep\n", encoding="utf-8")

            artifact_paths = []
            for index, suffix in enumerate(sorted(build_devkit.FORBIDDEN_SUFFIXES)):
                artifact = dirty / "src" / f"artifact-{index}{suffix.upper()}"
                artifact.write_bytes(f"artifact-{suffix}\n".encode("ascii"))
                artifact_paths.append(artifact)

            excluded: set[Path] = set()
            clean_files = build_devkit.relative_files(clean)
            dirty_files = build_devkit.relative_files(dirty, excluded_artifacts=excluded)

            self.assertEqual(set(clean_files), set(dirty_files))
            self.assertEqual({PurePosixPath("src/keep.c")}, set(dirty_files))
            self.assertEqual(set(artifact_paths), excluded)
            for artifact in artifact_paths:
                self.assertTrue(artifact.is_file())
                self.assertTrue(artifact.read_bytes().startswith(b"artifact-"))

    def test_poc_platform_directories_are_filtered(self) -> None:
        with tempfile.TemporaryDirectory() as workspace_raw:
            workspace = Path(workspace_raw)
            project = workspace / "poc" / "probe"
            (project / "src").mkdir(parents=True)
            (project / "win").mkdir()
            (project / "mac").mkdir()
            (workspace / "poc" / "_poc_template").mkdir()
            participant = workspace / "my" / "device1"
            (participant / "win").mkdir(parents=True)
            (participant / "mac").mkdir()
            (project / "src" / "common.c").write_text("common\n", encoding="utf-8")
            (project / "src" / "firmware.bin").write_bytes(b"generated\n")
            (project / "win" / "host.py").write_text("win\n", encoding="utf-8")
            (project / "mac" / "host.py").write_text("mac\n", encoding="utf-8")
            (workspace / "poc" / "_poc_template" / "README.md").write_text("organizer only\n", encoding="utf-8")
            (participant / "win" / "host.py").write_text("win\n", encoding="utf-8")
            (participant / "mac" / "host.py").write_text("mac\n", encoding="utf-8")
            (workspace / "deps" / "generated").mkdir(parents=True)
            (workspace / "deps" / "generated" / "tool.bin").write_bytes(b"generated")
            original = build_devkit.WORKSPACE
            try:
                build_devkit.WORKSPACE = workspace
                windows_excluded: set[Path] = set()
                macos_excluded: set[Path] = set()
                windows = build_devkit.merged_files("win", windows_excluded)
                macos = build_devkit.merged_files("mac", macos_excluded)
            finally:
                build_devkit.WORKSPACE = original
            base = PurePosixPath("workspace/poc/probe")
            self.assertIn(base / "src/common.c", windows)
            self.assertNotIn(base / "src/firmware.bin", windows)
            self.assertNotIn(base / "src/firmware.bin", macos)
            self.assertIn(project / "src" / "firmware.bin", windows_excluded)
            self.assertIn(project / "src" / "firmware.bin", macos_excluded)
            self.assertIn(base / "win/host.py", windows)
            self.assertNotIn(base / "mac/host.py", windows)
            self.assertIn(base / "src/common.c", macos)
            self.assertIn(base / "mac/host.py", macos)
            self.assertNotIn(base / "win/host.py", macos)
            self.assertNotIn(PurePosixPath("workspace/deps/generated/tool.bin"), windows)
            self.assertNotIn(PurePosixPath("workspace/deps/generated/tool.bin"), macos)
            self.assertNotIn(PurePosixPath("workspace/poc/_poc_template/README.md"), windows)
            self.assertNotIn(PurePosixPath("workspace/poc/_poc_template/README.md"), macos)
            self.assertIn(PurePosixPath("workspace/my/device1/win/host.py"), windows)
            self.assertNotIn(PurePosixPath("workspace/my/device1/mac/host.py"), windows)
            self.assertIn(PurePosixPath("workspace/my/device1/mac/host.py"), macos)
            self.assertNotIn(PurePosixPath("workspace/my/device1/win/host.py"), macos)


class DocumentBundleTests(unittest.TestCase):
    def test_slide_bundle_is_deterministic_and_compact(self) -> None:
        with tempfile.TemporaryDirectory() as output_raw:
            output = Path(output_raw)
            first = output / "first.zip"
            second = output / "second.zip"
            build_document_bundle.build(first, "slides")
            build_document_bundle.build(second, "slides")
            self.assertEqual(first.read_bytes(), second.read_bytes())

            with zipfile.ZipFile(first) as bundle:
                names = bundle.namelist()
                self.assertEqual("00_READ_ME_FIRST.md", names[0])
                for required in (
                    "docs/project/00_PROJECT_OVERVIEW.md",
                    "docs/project/40_WORKSHOP_GUIDE_RULES.md",
                    "workspace/ai/README.md",
                    "workspace/parts/PARTS_FOR_AI.md",
                    "workspace/exercises/00_onboard_led_blink/README.md",
                    "workspace/my/README.md",
                ):
                    self.assertIn(required, names)
                self.assertNotIn("docs/project/99_FULL_PROJECT_GUIDE.md", names)
                self.assertNotIn("docs/project/90_DECISIONS.md", names)
                self.assertFalse(any(name.startswith("workspace/poc/") for name in names))

    def test_full_profile_adds_internal_source_documents(self) -> None:
        with tempfile.TemporaryDirectory() as output_raw:
            archive = Path(output_raw) / "full.zip"
            build_document_bundle.build(archive, "full")
            with zipfile.ZipFile(archive) as bundle:
                names = bundle.namelist()
                self.assertIn("docs/project/90_DECISIONS.md", names)
                self.assertIn("docs/project/20_BUILD_RULES.md", names)
                self.assertNotIn("docs/project/99_FULL_PROJECT_GUIDE.md", names)


class NewPocTests(unittest.TestCase):
    def test_creates_common_project_from_template(self) -> None:
        with tempfile.TemporaryDirectory() as projects_raw:
            projects = Path(projects_raw)
            shutil.copytree(ROOT / "workspace" / "poc" / "_poc_template", projects / "_poc_template")
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

    def test_creates_device1_without_overwriting(self) -> None:
        with tempfile.TemporaryDirectory() as workspace_raw:
            workspace = Path(workspace_raw)
            shutil.copytree(ROOT / "workspace" / "ai", workspace / "ai")
            tool = workspace / "ai" / "new_my_device.py"
            first = subprocess.run(
                [sys.executable, str(tool), "--workspace", str(workspace)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, first.returncode, first.stdout + first.stderr)
            project = workspace / "my" / "device1"
            self.assertTrue((project / "Makefile").is_file())
            self.assertTrue((project / "REQUIREMENTS.md").is_file())

            second = subprocess.run(
                [sys.executable, str(tool), "--workspace", str(workspace)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, second.returncode)
            self.assertIn("上書きしません", second.stdout)


class UnifiedRepositoryTests(unittest.TestCase):
    def test_my_device_template_has_safe_buildable_layout(self) -> None:
        root = ROOT / "workspace" / "ai" / "MY_DEVICE_TEMPLATE"
        for relative in ("README.md", "REQUIREMENTS.md", "WIRING.md", "Makefile", "device1.c", "funconfig.h"):
            self.assertTrue((root / relative).is_file(), relative)

        makefile = (root / "Makefile").read_text(encoding="utf-8")
        source = (root / "device1.c").read_text(encoding="utf-8")
        wiring = (root / "WIRING.md").read_text(encoding="utf-8")
        self.assertIn("TARGET := device1", makefile)
        self.assertIn("TARGET_MCU := CH32V003", makefile)
        self.assertIn("funDigitalWrite(BUILTIN_LED_PIN, FUN_LOW)", source)
        self.assertNotIn("rv003usb", makefile)
        self.assertIn("状態: 未確認 / 確認済み", wiring)

    def test_program_generation_prompt_requires_human_wiring_approval(self) -> None:
        prompt = (ROOT / "workspace" / "ai" / "PROGRAM_GENERATION_PROMPT.md").read_text(encoding="utf-8")
        self.assertIn("## プログラム生成開始条件", prompt)
        self.assertIn("自ら「配線安全確認」を`確認済み`へ変更してはいけません", prompt)
        self.assertIn("実行可能なコードを生成してはいけません", prompt)
        self.assertIn("`device1.zip`を生成しないでください", prompt)

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
            "03_vibration_motor_console": ("vibration_motor_console.c", "usb_config.h", "haptic_pattern.h", "haptic_pattern_protocol.h", "host/motorctl.py"),
            "04_rotary_cursor_haptic": ("rotary_cursor_size.c", "usb_config.h", "haptic_pattern.h", "haptic_pattern_protocol.h"),
        }
        for exercise, files in requirements.items():
            root = ROOT / "workspace" / "exercises" / exercise
            self.assertTrue((root / "Makefile").is_file())
            for relative in files:
                self.assertTrue((root / relative).is_file(), f"{exercise}/{relative}")
            self.assertFalse((root / "win").exists())
            self.assertFalse((root / "mac").exists())

        rotary_host = ROOT / "workspace" / "exercises" / "02_rotary_cursor_size" / "host"
        self.assertTrue((rotary_host / "cursor_size_host.py").is_file())
        self.assertFalse((rotary_host / "win").exists())
        self.assertFalse((rotary_host / "mac").exists())

        motor_host = ROOT / "workspace" / "exercises" / "03_vibration_motor_console" / "host"
        self.assertTrue((motor_host / "motorctl.py").is_file())
        self.assertFalse((motor_host / "win").exists())
        self.assertFalse((motor_host / "mac").exists())

        haptic_host = ROOT / "workspace" / "exercises" / "04_rotary_cursor_haptic" / "host"
        self.assertTrue((haptic_host / "cursor_size_host.py").is_file())
        self.assertFalse((haptic_host / "win").exists())
        self.assertFalse((haptic_host / "mac").exists())

        plain = (ROOT / "workspace" / "exercises" / "02_rotary_cursor_size" / "rotary_cursor_size.c").read_text(encoding="utf-8")
        blink = (ROOT / "workspace" / "exercises" / "00_onboard_led_blink" / "onboard_led_blink.c").read_text(encoding="utf-8")
        motor = (ROOT / "workspace" / "exercises" / "03_vibration_motor_console" / "vibration_motor_console.c").read_text(encoding="utf-8")
        haptic = (ROOT / "workspace" / "exercises" / "04_rotary_cursor_haptic" / "rotary_cursor_size.c").read_text(encoding="utf-8")
        self.assertNotIn("HAPTIC_PIN", plain)
        self.assertIn("MOTOR_PIN", motor)
        self.assertIn("HAPTIC_PIN", haptic)
        self.assertIn("#define BLINK_ON_MS 150u", blink)
        self.assertIn("#define BLINK_GAP_MS 150u", blink)
        self.assertIn("#define BLINK_PAUSE_MS 1500u", blink)
        self.assertIn("#define BLINK_FLASH_COUNT 3u", blink)
        self.assertIn("#define BUILTIN_LED_ON FUN_HIGH", blink)
        self.assertIn("#define BUILTIN_LED_OFF FUN_LOW", blink)

        motor_root = ROOT / "workspace" / "exercises" / "03_vibration_motor_console"
        haptic_root = ROOT / "workspace" / "exercises" / "04_rotary_cursor_haptic"
        for shared_name in ("haptic_pattern.h", "haptic_pattern_protocol.h"):
            self.assertEqual(
                (motor_root / shared_name).read_bytes(),
                (haptic_root / shared_name).read_bytes(),
                f"03/04 shared haptic implementation differs: {shared_name}",
            )

    def test_macos_setup_builds_write_tool(self) -> None:
        setup = (ROOT / "scripts" / "setup.sh").read_text(encoding="utf-8")
        self.assertIn('scripts/build-minichlink.sh', setup)
        self.assertIn('UIAP_RUNTIME/bin/minichlink', setup)


if __name__ == "__main__":
    unittest.main()
