import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import sync_toastmasters_terminology as terminology


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("references/toastmasters-terminology.md")
POSTER = "skills/poster-image-translation-redesign/references/toastmasters-terminology.md"
POWERPOINT = "skills/powerpoint-translation-redesign/references/toastmasters-terminology.md"
MENTOR = "skills/egg-toastmasters-speech-mentor/references/d85-toastmasters-terminology.md"
SAMPLE = "# Glossary\n\n| Club Officer | 俱乐部官员 |\n"


class ToastmastersTerminology(unittest.TestCase):
    def make_repo(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        (root / SOURCE).parent.mkdir()
        (root / SOURCE).write_text(SAMPLE, encoding="utf-8")
        return root

    def assert_mirror(self, root, mirror, canonical):
        notice, body = (root / mirror).read_bytes().split(b"\n\n", 1)
        self.assertIn(SOURCE.as_posix().encode(), notice)
        self.assertIn(b"do not edit", notice.lower())
        self.assertEqual(body, canonical)

    def test_checked_in_mirrors_match_canonical(self):
        self.assertEqual(terminology.sync(ROOT, check=True), [])
        canonical = (ROOT / SOURCE).read_bytes()
        for mirror in (POSTER, POWERPOINT, MENTOR):
            with self.subTest(mirror=mirror):
                self.assert_mirror(ROOT, mirror, canonical)

    def test_sync_repairs_drift(self):
        root = self.make_repo()
        poster = root / POSTER
        poster.parent.mkdir(parents=True)
        poster.write_text("stale", encoding="utf-8")

        self.assertEqual(terminology.sync(root, check=False), [])

        self.assertEqual((root / SOURCE).read_bytes(), SAMPLE.encode())
        for mirror in (POSTER, POWERPOINT, MENTOR):
            with self.subTest(mirror=mirror):
                self.assert_mirror(root, mirror, SAMPLE.encode())

    def test_check_reports_missing_and_drifted_mirrors(self):
        root = self.make_repo()
        poster = root / POSTER
        poster.parent.mkdir(parents=True)
        poster.write_text("stale", encoding="utf-8")
        modified = poster.stat().st_mtime_ns

        self.assertCountEqual(terminology.sync(root, check=True), [POSTER, POWERPOINT, MENTOR])

        self.assertEqual(poster.read_bytes(), b"stale")
        self.assertEqual(poster.stat().st_mtime_ns, modified)
        self.assertFalse((root / POWERPOINT).parent.exists())
        self.assertFalse((root / MENTOR).parent.exists())
        self.assertEqual((root / SOURCE).read_bytes(), SAMPLE.encode())

    def test_sync_rejects_symlink_destination(self):
        root = self.make_repo()
        target = root / "untouched.md"
        target.write_text("untouched", encoding="utf-8")
        link = root / POWERPOINT
        link.parent.mkdir(parents=True)
        link.symlink_to(target)

        for check in (True, False):
            with self.subTest(check=check):
                with self.assertRaises(ValueError) as error:
                    terminology.sync(root, check=check)
                self.assertEqual(str(error.exception), f"Symlink destination: {POWERPOINT}")
                self.assertEqual(target.read_bytes(), b"untouched")
                self.assertTrue(link.is_symlink())
                self.assertFalse((root / POSTER).parent.exists())

    def test_mirror_destinations_stay_under_skill_reference_directories(self):
        root = self.make_repo()
        for path in (
            Path("references/not-a-mirror.md"),
            Path("skills/example/references/../not-a-mirror.md"),
            root / "skills/example/references/absolute.md",
        ):
            with self.subTest(path=path), patch.object(terminology, "MIRRORS", (path,)):
                with self.assertRaises(ValueError) as error:
                    terminology.sync(root, check=False)
                self.assertEqual(str(error.exception), f"Invalid mirror destination: {path.as_posix()}")
        self.assertFalse((root / "skills").exists())

        redirect = root / "redirect"
        redirect.mkdir()
        parent = (root / POSTER).parent
        parent.parent.mkdir(parents=True)
        parent.symlink_to(redirect, target_is_directory=True)
        with self.assertRaises(ValueError) as error:
            terminology.sync(root, check=False)
        self.assertEqual(str(error.exception), f"Symlink destination: {POSTER}")
        self.assertEqual(list(redirect.iterdir()), [])

    def test_missing_canonical_names_source_and_does_not_write(self):
        root = self.make_repo()
        (root / SOURCE).unlink()

        with self.assertRaises(FileNotFoundError) as error:
            terminology.sync(root, check=False)

        self.assertEqual(str(error.exception), f"Missing canonical glossary: {SOURCE.as_posix()}")
        self.assertFalse((root / "skills").exists())
