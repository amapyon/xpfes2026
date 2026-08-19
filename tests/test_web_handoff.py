from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]


class WebHandoffTests(unittest.TestCase):
    def make_workspace(self, root: Path) -> Path:
        workspace = root / "workspace"
        shutil.copytree(ROOT / "workspace" / "ai", workspace / "ai")
        shutil.copytree(ROOT / "workspace" / "parts", workspace / "parts")
        shutil.copytree(ROOT / "workspace" / "ai" / "MY_DEVICE_TEMPLATE", workspace / "my" / "device1")
        (workspace / "exercises" / "sample").mkdir(parents=True)
        (workspace / "exercises" / "sample" / "README.md").write_text("sample\n", encoding="utf-8")
        (workspace / "exercises" / "sample" / "sample.c").write_text("int main(void) {}\n", encoding="utf-8")
        (workspace / "exercises" / "sample" / "sample.elf").write_bytes(b"generated")
        return workspace

    def run_tool(self, workspace: Path, *args: str) -> subprocess.CompletedProcess[str]:
        subprocess_env = os.environ.copy()
        subprocess_env["PYTHONIOENCODING"] = "cp1252"
        return subprocess.run(
            [sys.executable, str(workspace / "ai" / "prepare_web_handoff.py"), "--workspace", str(workspace), *args],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=subprocess_env,
        )

    def test_creates_folder_markdown_and_zip_with_auto_reference(self) -> None:
        with tempfile.TemporaryDirectory() as root_raw:
            workspace = self.make_workspace(Path(root_raw))
            requirements = workspace / "my" / "device1" / "REQUIREMENTS.md"
            requirements.write_text(
                requirements.read_text(encoding="utf-8") + "\n`workspace/exercises/sample`\n",
                encoding="utf-8",
            )
            result = self.run_tool(workspace)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            output = workspace / "my" / "WEB_HANDOFF_device1"
            upload = output / "UPLOAD_THIS_FOLDER"
            manifest = (upload / "AI_HANDOFF_MANIFEST.md").read_text(encoding="utf-8")
            self.assertIn("workspace/exercises/sample", manifest)
            self.assertIn("workspace/exercises/sample/sample.elf", manifest)
            self.assertTrue((upload / "sources/workspace/exercises/sample/sample.c").is_file())
            self.assertFalse((upload / "sources/workspace/exercises/sample/sample.elf").exists())
            self.assertTrue((upload / "sources/workspace/my/device1/device1.c").is_file())
            self.assertTrue((output / "AI_HANDOFF.md").is_file())
            self.assertTrue((output / "AI_HANDOFF.zip").is_file())
            with zipfile.ZipFile(output / "AI_HANDOFF.zip") as archive:
                self.assertIn("AI_HANDOFF/AI_HANDOFF_MANIFEST.md", archive.namelist())
                self.assertIn("AI_HANDOFF/sources/workspace/ai/MY_DEVICE_TEMPLATE/Makefile", archive.namelist())

    def test_manifest_hash_matches_copied_source(self) -> None:
        with tempfile.TemporaryDirectory() as root_raw:
            workspace = self.make_workspace(Path(root_raw))
            result = self.run_tool(workspace)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            output = workspace / "my" / "WEB_HANDOFF_device1" / "UPLOAD_THIS_FOLDER"
            copied = output / "sources/workspace/ai/BOARD_FOR_AI.md"
            digest = hashlib.sha256(copied.read_bytes()).hexdigest()
            manifest = (output / "AI_HANDOFF_MANIFEST.md").read_text(encoding="utf-8")
            self.assertIn(digest, manifest)

    def test_refuses_to_replace_output_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as root_raw:
            workspace = self.make_workspace(Path(root_raw))
            self.assertEqual(0, self.run_tool(workspace).returncode)
            second = self.run_tool(workspace)
            self.assertEqual(1, second.returncode)
            self.assertIn("--force", second.stdout)
            self.assertEqual(0, self.run_tool(workspace, "--force").returncode)

    def test_rejects_reference_outside_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as root_raw:
            workspace = self.make_workspace(Path(root_raw))
            result = self.run_tool(workspace, "--reference", "deps/ch32fun")
            self.assertEqual(1, result.returncode)
            self.assertIn("exercises/<名前>", result.stdout)

    def test_rejects_output_inside_device(self) -> None:
        with tempfile.TemporaryDirectory() as root_raw:
            workspace = self.make_workspace(Path(root_raw))
            output = workspace / "my" / "device1" / "handoff"
            result = self.run_tool(workspace, "--output", str(output))
            self.assertEqual(1, result.returncode)
            self.assertIn("device1外", result.stdout)

    def test_rejects_secret_in_selected_reference(self) -> None:
        with tempfile.TemporaryDirectory() as root_raw:
            workspace = self.make_workspace(Path(root_raw))
            (workspace / "exercises" / "sample" / ".env").write_text("TOKEN=secret\n", encoding="utf-8")
            result = self.run_tool(workspace, "--reference", "exercises/sample")
            self.assertEqual(1, result.returncode)
            self.assertIn("秘密情報", result.stdout)
            self.assertFalse((workspace / "my" / "WEB_HANDOFF_device1").exists())


if __name__ == "__main__":
    unittest.main()
