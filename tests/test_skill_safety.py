"""Tests for the best-effort skill safety scanner (scripts/scan_skill_safety.py)."""

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "scan_skill_safety", ROOT / "scripts/scan_skill_safety.py"
)
SCANNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCANNER)


def blocks(text, relpath="skills/demo/SKILL.md"):
    return [m for level, m in SCANNER.scan_text(text, relpath) if level == "block"]


def warns(text, relpath="skills/demo/SKILL.md"):
    return [m for level, m in SCANNER.scan_text(text, relpath) if level == "warn"]


class SkillSafetyScanner(unittest.TestCase):
    def test_clean_skill_passes(self):
        text = "# Demo skill\n\nTurn notes into minutes. Ask for owners instead of inventing them.\n"
        self.assertEqual(SCANNER.scan_text(text, "skills/demo/SKILL.md"), [])

    def test_aws_key_blocked(self):
        self.assertTrue(blocks("key = " + "AKIA" + "IOSFODNN7EXAMPLE"))

    def test_github_pat_blocked(self):
        self.assertTrue(blocks("token: ghp_" + "A" * 36))

    def test_fine_grained_github_pat_blocked(self):
        self.assertTrue(blocks("github_" + "pat_" + "A" * 82))

    def test_private_key_block_blocked(self):
        self.assertTrue(blocks("-----BEGIN " + "OPENSSH " + "PRIVATE KEY-----"))

    def test_slack_token_blocked(self):
        self.assertTrue(blocks("xoxb-" + "A" * 20))

    def test_env_file_name_blocked(self):
        self.assertTrue(blocks("anything", relpath="skills/demo/.env"))

    def test_credential_extensions_blocked(self):
        for name in ("service-account.key", "certificate.pem"):
            with self.subTest(name=name):
                self.assertTrue(blocks("anything", relpath="skills/demo/" + name))

    def test_macos_private_path_blocked(self):
        self.assertTrue(blocks("read /Users/" + "alice" + "/Documents/private.txt"))

    def test_windows_private_path_blocked(self):
        self.assertTrue(blocks("copy C:\\Users\\" + "alice" + "\\Desktop\\a.png"))

    def test_generic_home_path_warns_not_blocks(self):
        sample = "load " + chr(126) + "/.config/demo.json"
        self.assertFalse(blocks(sample))
        self.assertTrue(warns(sample))

    def test_placeholder_assignment_not_flagged(self):
        text = "set api_key = YOUR_EXAMPLE_KEY_HERE and continue"
        self.assertEqual(warns(text), [])

    def test_long_credential_assignment_warns(self):
        text = "password = " + "S3cretValue9f2k1m8x7q4w3e5r6"
        self.assertTrue(warns(text))

    def test_network_capable_script_warns(self):
        text = "import " + "urllib.request"
        self.assertTrue(warns(text, relpath="skills/demo/scripts/fetch.py"))
        self.assertEqual(warns(text, relpath="skills/demo/SKILL.md"), [])

    def test_binary_content_warns(self):
        self.assertTrue(
            SCANNER.scan_bytes(b"\x89PNG\x00\x00\x00 rest", "skills/demo/photo.png")
        )
        self.assertEqual(SCANNER.scan_bytes(b"plain text", "skills/demo/SKILL.md"), [])


class SkillSafetyGitIntegration(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "core.quotepath", "true")
        self.git("-c", "user.name=Scanner test", "-c", "user.email=test@example.invalid",
                 "commit", "--allow-empty", "-qm", "base")

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.repo, text=True).strip()

    def commit(self):
        self.git("add", "-A")
        self.git("-c", "user.name=Scanner test", "-c", "user.email=test@example.invalid",
                 "commit", "-qm", "fixture")
        return self.git("rev-parse", "HEAD")

    def scan(self, base):
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts/scan_skill_safety.py")],
            cwd=self.repo, env={**os.environ, "BASE_SHA": base},
            capture_output=True, text=True,
        )

    def test_special_filenames_are_scanned(self):
        base = self.git("rev-parse", "HEAD")
        for name in ("测试.md", "quoted\nfile.md", "carriage\rreturn.md", " leading-and-trailing.md "):
            with self.subTest(name=name):
                path = self.repo / name
                path.write_text("ghp_" + "A" * 36)
                self.commit()
                result = self.scan(base)
                self.assertEqual(result.returncode, 1, result.stdout)
                path.unlink()
                self.commit()

    def assert_changed_symlink_blocked(self, existing_symlink):
        target = self.repo / "target.md"
        target.write_text("Clean target")
        link = self.repo / "link.md"
        if existing_symlink:
            link.symlink_to("target.md")
        else:
            link.write_text("Regular file")
        base = self.commit()
        link.unlink()
        # A dangling link proves scanning does not depend on reading its target.
        link.symlink_to("missing-target.md")
        self.commit()
        result = self.scan(base)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("symlink", result.stdout)

    def test_file_converted_to_symlink_is_rejected(self):
        self.assert_changed_symlink_blocked(False)

    def test_modified_symlink_is_rejected(self):
        self.assert_changed_symlink_blocked(True)

    def test_deleted_files_are_not_reported_as_unreadable(self):
        path = self.repo / "deleted.md"
        path.write_text("Clean content")
        base = self.commit()
        path.unlink()
        self.commit()
        result = self.scan(base)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("not readable", result.stdout)


if __name__ == "__main__":
    unittest.main()
