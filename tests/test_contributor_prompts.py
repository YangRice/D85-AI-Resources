"""Behavioral contracts for per-skill prompt starters and portable packaging."""

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "contributor_prompt_builder", ROOT / "scripts/build_portable_prompts.py"
)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


class PromptInputFields(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        for skill_id in ("example", "find-tmcompanion-tool"):
            folder = root / "skills" / skill_id
            folder.mkdir(parents=True)
            for filename in ("SKILL.md", "SKILL.zh.md"):
                (folder / filename).write_text(
                    f"---\nname: {skill_id}\ndescription: Example\n---\nTest body.\n",
                    encoding="utf-8",
                )
        self.root_patch = patch.object(BUILDER, "ROOT", root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def starter(self, item, lang):
        output = BUILDER.build_prompt(item, lang)
        return output.split("```text\n", 1)[1].split("\n```", 1)[0].splitlines()

    def test_language_specific_fields_preserve_order(self):
        fields = {"en": ["Local source:", "Useful outcome:"], "zh": ["本地来源：", "实际用途："]}
        item = {"id": "example", "version": "1", "input_fields": fields}
        for lang in ("en", "zh"):
            with self.subTest(lang=lang):
                self.assertEqual(self.starter(item, lang), fields[lang])

    def test_missing_language_uses_existing_default(self):
        item = {"id": "example", "version": "1", "input_fields": {"en": ["Source:"]}}
        self.assertEqual(self.starter(item, "zh"), BUILDER.LANG["zh"]["fields"])

    def test_existing_general_and_tool_finder_starters_are_preserved(self):
        for lang in ("en", "zh"):
            for skill_id, expected in (
                ("example", BUILDER.LANG[lang]["fields"]),
                ("find-tmcompanion-tool", BUILDER.TOOL_FINDER_FIELDS[lang]),
            ):
                with self.subTest(lang=lang, skill_id=skill_id):
                    self.assertEqual(self.starter({"id": skill_id, "version": "1"}, lang), expected)

    def test_invalid_custom_fields_raise_clear_error(self):
        for fields in ([], "Source:", [None], [""], ["  "], ["Source:\nUnexpected line"], ["Source:\n"]):
            with self.subTest(fields=fields):
                with self.assertRaisesRegex(ValueError, "input_fields"):
                    self.starter({"id": "example", "version": "1", "input_fields": {"en": fields}}, "en")

    def test_invalid_language_mapping_raises_clear_error(self):
        for overrides in (None, [], "Source:"):
            with self.subTest(overrides=overrides):
                with self.assertRaisesRegex(ValueError, "input_fields"):
                    self.starter({"id": "example", "version": "1", "input_fields": overrides}, "en")


class ContributorPortablePackage(unittest.TestCase):
    def test_generated_prompts_include_policy_and_have_no_local_reference_dependency(self):
        item = next(s for s in BUILDER.CATALOG["skills"] if s["id"] == "d85-skill-contributor")
        for lang in ("en", "zh"):
            with self.subTest(lang=lang):
                result = BUILDER.build_prompt(item, lang)
                rules = (ROOT / "skills/d85-skill-contributor/references" / f"contribution-rules.{lang}.md").read_text(encoding="utf-8").strip()
                self.assertEqual(result.count(rules), 1)
                self.assertNotIn(
                    f"(references/contribution-rules.{lang}.md)", result
                )
                self.assertEqual(
                    result,
                    (ROOT / "prompts" / f"d85-skill-contributor.{lang}.md").read_text(encoding="utf-8"),
                )
                fields = result.split("```text\n", 1)[1].split("\n```", 1)[0].splitlines()
                self.assertEqual(fields, item["input_fields"][lang])


if __name__ == "__main__":
    unittest.main()
