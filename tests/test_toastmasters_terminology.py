import json
import re
import shutil
import subprocess
import sys
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
PDF = "skills/translate-pdf/references/toastmasters-terminology.md"
PDF_PATHWAYS = "skills/translate-pdf/references/pathways-terminology.md"
CONSUMERS = (POSTER, POWERPOINT, MENTOR, PDF)
TRANSLATION_PROMPTS = ("translate-pdf", "powerpoint-translation-redesign")
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
        path = root / mirror
        self.assertTrue(path.is_file(), mirror)
        notice, body = path.read_bytes().split(b"\n\n", 1)
        self.assertIn(SOURCE.as_posix().encode(), notice)
        self.assertIn(b"do not edit", notice.lower())
        self.assertEqual(body, canonical)

    def test_checked_in_mirrors_match_canonical(self):
        self.assertEqual(terminology.sync(ROOT, check=True), [])
        canonical = (ROOT / SOURCE).read_bytes()
        for mirror in CONSUMERS:
            with self.subTest(mirror=mirror):
                self.assert_mirror(ROOT, mirror, canonical)

    def test_every_core_glossary_consumer_is_synchronized(self):
        self.assertCountEqual(terminology.MIRRORS, map(Path, CONSUMERS))

    def test_translation_glossary_links_work_in_independent_packages(self):
        glossary = "references/toastmasters-terminology.md"
        for mirror in (POSTER, POWERPOINT, PDF):
            source = ROOT / Path(mirror).parents[1]
            with self.subTest(skill=source.name), tempfile.TemporaryDirectory() as temp:
                package = Path(temp) / source.name
                shutil.copytree(source, package, symlinks=True)
                instruction = (package / "SKILL.md").read_text(encoding="utf-8")
                expected = [glossary]
                if mirror == PDF:
                    expected.append("references/pathways-terminology.md")
                targets = re.findall(r"\]\(([^)]*terminology\.md)\)", instruction)
                self.assertCountEqual(targets, expected)
                for target in targets:
                    file = (package / target).resolve()
                    self.assertTrue(file.is_relative_to(package.resolve()))
                    self.assertTrue(file.is_file(), target)
                self.assert_mirror(Path(temp), f"{source.name}/{glossary}", (ROOT / SOURCE).read_bytes())

    def test_pdf_pathways_aliases_are_separate_from_core_glossary(self):
        supplement = ROOT / PDF_PATHWAYS
        self.assertTrue(supplement.is_file(), PDF_PATHWAYS)
        pathways = supplement.read_text(encoding="utf-8")
        core = (ROOT / PDF).read_text(encoding="utf-8")
        for alias in (
            "必修 = Required",
            "掌握基础 = Mastering Fundamentals",
            "动态领导 = Dynamic Leadership",
            "初试啼声 = Ice Breaker",
            "反思你的学习路径 = Reflect on Your Path",
            "杰出会员 = Distinguished Toastmaster (DTM)",
        ):
            with self.subTest(alias=alias):
                self.assertIn(alias, pathways)
                self.assertNotIn(alias, core)

    def make_prompt_repo(self):
        root = self.make_repo()
        (root / SOURCE).write_bytes((ROOT / SOURCE).read_bytes())
        (root / "scripts").mkdir()
        for filename in ("build_portable_prompts.py", "sync_toastmasters_terminology.py"):
            shutil.copy2(ROOT / "scripts" / filename, root / "scripts" / filename)
        shutil.copytree(ROOT / "catalog", root / "catalog")
        catalog_path = root / "catalog/skills.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog["skills"] = []
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
        for skill_id in TRANSLATION_PROMPTS:
            shutil.copytree(ROOT / "skills" / skill_id, root / "skills" / skill_id)
        return root

    def generate_translation_prompts(self, root):
        result = subprocess.run(
            [sys.executable, "scripts/build_portable_prompts.py"],
            cwd=root, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        paths = {skill_id: root / "prompts" / f"{skill_id}.md" for skill_id in TRANSLATION_PROMPTS}
        self.assertEqual([skill_id for skill_id, path in paths.items() if path.is_file()], list(paths))
        return {skill_id: path.read_text(encoding="utf-8") for skill_id, path in paths.items()}

    def test_standalone_translation_prompts_match_generated_offline_content(self):
        outputs = self.generate_translation_prompts(self.make_prompt_repo())
        core = (ROOT / SOURCE).read_text(encoding="utf-8").strip()
        supplement = (ROOT / PDF_PATHWAYS).read_text(encoding="utf-8").strip()
        for skill_id, output in outputs.items():
            with self.subTest(skill=skill_id):
                checked_in = (ROOT / "prompts" / f"{skill_id}.md").read_text(encoding="utf-8")
                self.assertEqual(checked_in, output)
                self.assertEqual(output.count(core), 1)
                self.assertNotRegex(output, r"\]\([^)]*terminology\.md\)")
        self.assertEqual(outputs["translate-pdf"].count(supplement), 1)
        self.assertIn("初试啼声 = Ice Breaker", outputs["translate-pdf"])
        self.assertNotIn(supplement, outputs["powerpoint-translation-redesign"])

    def test_build_refreshes_stale_mirrors_before_embedding(self):
        root = self.make_prompt_repo()
        new_term = "| Fixture Term | 测试术语 |"
        glossary = (root / SOURCE).read_text(encoding="utf-8") + new_term + "\n"
        (root / SOURCE).write_text(glossary, encoding="utf-8")
        self.assertNotIn(new_term, (root / PDF).read_text(encoding="utf-8"))
        self.assertNotIn(new_term, (root / POWERPOINT).read_text(encoding="utf-8"))

        outputs = self.generate_translation_prompts(root)

        for mirror in CONSUMERS:
            self.assert_mirror(root, mirror, glossary.encode())
        for output in outputs.values():
            self.assertEqual(output.count(new_term), 1)

    def test_sync_repairs_drift(self):
        root = self.make_repo()
        poster = root / POSTER
        poster.parent.mkdir(parents=True)
        poster.write_text("stale", encoding="utf-8")

        self.assertEqual(terminology.sync(root, check=False), [])

        self.assertEqual((root / SOURCE).read_bytes(), SAMPLE.encode())
        for mirror in CONSUMERS:
            with self.subTest(mirror=mirror):
                self.assert_mirror(root, mirror, SAMPLE.encode())

    def test_check_reports_missing_and_drifted_mirrors(self):
        root = self.make_repo()
        poster = root / POSTER
        poster.parent.mkdir(parents=True)
        poster.write_text("stale", encoding="utf-8")
        modified = poster.stat().st_mtime_ns

        self.assertCountEqual(terminology.sync(root, check=True), CONSUMERS)

        self.assertEqual(poster.read_bytes(), b"stale")
        self.assertEqual(poster.stat().st_mtime_ns, modified)
        for mirror in (POWERPOINT, MENTOR, PDF):
            self.assertFalse((root / mirror).parent.exists())
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
