"""Portable packaging contracts, not certification of coaching behavior."""

import importlib.util
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SKILL_ID = "prepare-successful-club-presentation"
SPEC = importlib.util.spec_from_file_location(
    "scs_prompt_builder", ROOT / "scripts/build_portable_prompts.py"
)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)
ITEM = next(item for item in BUILDER.CATALOG["skills"] if item["id"] == SKILL_ID)


class SuccessfulClubPortablePackage(unittest.TestCase):
    def test_each_language_bundles_every_declared_reference_once(self):
        for lang in ("en", "zh"):
            with self.subTest(lang=lang):
                output = BUILDER.build_prompt(ITEM, lang)
                for template in ITEM["portable_references"]:
                    ref = ROOT / "skills" / SKILL_ID / "references" / template.format(lang=lang)
                    self.assertEqual(output.count(ref.read_text(encoding="utf-8").strip()), 1)
                self.assertNotRegex(output, r"\]\(references/[^)]+\)")
                self.assertNotIn("`action:", output)

    def test_generated_editions_equal_canonical_build(self):
        for lang in ("en", "zh"):
            with self.subTest(lang=lang):
                self.assertEqual(
                    BUILDER.build_prompt(ITEM, lang),
                    (ROOT / "prompts" / f"{SKILL_ID}.{lang}.md").read_text(encoding="utf-8"),
                )

    def test_package_works_without_repository_shared_files_or_other_skills(self):
        with tempfile.TemporaryDirectory() as temp:
            isolated = Path(temp)
            shutil.copytree(ROOT / "skills" / SKILL_ID, isolated / "skills" / SKILL_ID)
            self.assertEqual(ITEM["requires"], [])
            self.assertEqual(ITEM["recommends"], [])
            self.assertEqual(ITEM["actions"], [])
            for lang in ("en", "zh"):
                expected = BUILDER.build_prompt(ITEM, lang)
                with patch.object(BUILDER, "ROOT", isolated), patch.object(BUILDER, "CATALOG", {"skills": [ITEM]}):
                    self.assertEqual(BUILDER.build_prompt(ITEM, lang), expected)

    def test_language_pairs_reference_same_public_authorities(self):
        urls = lambda text: set(re.findall(r"https://[^\s)\]|]+", text))
        for template in ITEM["portable_references"]:
            with self.subTest(reference=template):
                folder = ROOT / "skills" / SKILL_ID / "references"
                self.assertEqual(
                    urls((folder / template.format(lang="en")).read_text(encoding="utf-8")),
                    urls((folder / template.format(lang="zh")).read_text(encoding="utf-8")),
                )


if __name__ == "__main__":
    unittest.main()
