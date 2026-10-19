"""Exercise package failures using isolated tracked exports, without installing skills."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/validate_skill_packages.py"


class SkillPackages(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.files = []
        self.write("skills/example/SKILL.md", "---\nname: example\ndescription: Example workflow.\n---\nRead [rules](references/rules.md).\n")
        self.write("skills/example/references/rules.md", "Keep the source intact.\n")
        self.write("skills/example/assets/template.docx", "template fixture")

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        self.files.append(name)

    def run_check(self):
        manifest = self.root / "tracked-files.txt"
        manifest.write_text("\n".join(self.files), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root), "--tracked-files", str(manifest)],
            capture_output=True, text=True,
        )

    def test_clean_export_passes_without_git_or_runtime_dependencies(self):
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Validated 1 skill package", result.stdout)
        self.assertIn("static", result.stdout.lower())

    def test_missing_bundled_reference_is_actionable(self):
        (self.root / "skills/example/references/rules.md").unlink()
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("skills/example/references/rules.md", result.stdout)

    def test_missing_template_is_detected_even_without_a_link(self):
        (self.root / "skills/example/assets/template.docx").unlink()
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("assets/template.docx", result.stdout)

    def test_identity_mismatch_fails(self):
        (self.root / "skills/example/SKILL.md").write_text("---\nname: another\ndescription: Example.\n---\n")
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("example", result.stdout)
        self.assertIn("another", result.stdout)

    def test_translated_identity_and_description_are_checked(self):
        self.write("skills/example/SKILL.zh.md", "---\nname: wrong\ndescription:\n---\n中文。\n")
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("SKILL.zh.md", result.stdout)

    def test_translated_prose_guide_does_not_need_native_frontmatter(self):
        self.write("skills/example/SKILL.zh.md", "# 使用指南\n中文说明。\n")
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_missing_frontmatter_fails(self):
        (self.root / "skills/example/SKILL.md").write_text("# Example\n")
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("frontmatter", result.stdout)

    def test_new_broken_local_link_fails(self):
        with (self.root / "skills/example/references/rules.md").open("a") as stream:
            stream.write("Read [more](missing.md).\n")
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing.md", result.stdout)

    def test_missing_catalog_companion_fails(self):
        self.write("catalog/skills.json", json.dumps({"skills": [{"id": "example", "requires": ["reviewer"], "recommends": []}]}))
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("reviewer", result.stdout)

    def test_missing_linked_conditional_companion_fails(self):
        with (self.root / "skills/example/SKILL.md").open("a") as stream:
            stream.write("For visual editing use [editor](../editor/SKILL.md).\n")
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("editor/SKILL.md", result.stdout)

    def test_missing_native_raster_companion_fails(self):
        self.write("skills/powerpoint-translation-redesign/SKILL.md", "---\nname: powerpoint-translation-redesign\ndescription: Translate slides.\n---\n")
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("poster-image-translation-redesign", result.stdout)

    def test_external_links_do_not_require_local_installations(self):
        with (self.root / "skills/example/SKILL.md").open("a") as stream:
            stream.write("Use the installed `presentations` skill. See [upstream](https://example.org/code).\n")
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_native_poster_workflow_requires_its_collection_companions(self):
        self.write("skills/poster-image-translation-redesign/SKILL.md", "---\nname: poster-image-translation-redesign\ndescription: Translate posters.\n---\n")
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        for companion in ("toastmasters-poster-maker", "toastmasters-poster-reviewer", "edit-svg-canvas"):
            self.assertIn(companion, result.stdout)
            self.write(f"skills/{companion}/SKILL.md", f"---\nname: {companion}\ndescription: Companion.\n---\n")
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout)

    @unittest.skipUnless((ROOT / ".git").exists(), "checkout discovery needs Git metadata; export checks use an explicit manifest")
    def test_untracked_artifacts_are_ignored_in_checkout(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(ROOT)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        tracked = subprocess.check_output(["git", "ls-files", "skills/*/SKILL.md"], cwd=ROOT, text=True).splitlines()
        self.assertIn(f"Validated {len(tracked)} skill package", result.stdout)
        self.assertNotIn("simulation-output.md", result.stdout)


if __name__ == "__main__":
    unittest.main()
