"""Tests for the best-effort skill safety scanner (scripts/scan_skill_safety.py)."""

import importlib.util
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


if __name__ == "__main__":
    unittest.main()
