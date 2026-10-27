import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class PosterResources(unittest.TestCase):
    def test_retired_packages_are_not_recreated_by_reference_sync(self):
        module = load('sync', ROOT / 'scripts/sync_poster_references.py')
        with tempfile.TemporaryDirectory() as td:
            module.ROOT = root = Path(td)
            canonical = root / 'references/toastmasters-brand'
            canonical.mkdir(parents=True)
            (canonical / 'asset-sources.json').write_bytes(
                (ROOT / 'references/toastmasters-brand/asset-sources.json').read_bytes())
            import sys
            from unittest.mock import patch
            with patch.object(sys, 'argv', ['sync_poster_references.py']):
                self.assertEqual(module.main(), 0)
            self.assertTrue((root / 'materials/toastmasters-brand/README.md').is_file())
            self.assertFalse((root / 'skills').exists())

    def test_retired_ids_are_absent_and_editor_remains_independent(self):
        catalog = json.loads((ROOT / 'catalog/skills.json').read_text())['skills']
        ids = {item['id'] for item in catalog}
        for name in ('toastmasters-poster-maker', 'toastmasters-poster-reviewer'):
            self.assertNotIn(name, ids)
            self.assertFalse((ROOT / 'skills' / name).exists())
            for lang in ('en', 'zh'):
                self.assertFalse((ROOT / 'prompts' / f'{name}.{lang}.md').exists())
        editor = next(item for item in catalog if item['id'] == 'edit-svg-canvas')
        self.assertEqual(editor['requires'], [])
        self.assertTrue((ROOT / 'skills/edit-svg-canvas/scripts/edit_svg.py').is_file())

    def test_materials_catalog_contains_every_saved_source(self):
        canonical = json.loads((ROOT/'references/toastmasters-brand/asset-sources.json').read_text())
        index = ROOT/'materials/toastmasters-brand/README.md'
        self.assertTrue(index.exists(), 'materials entry point missing')
        saved = ROOT/'materials/toastmasters-brand/sources.json'
        self.assertTrue(saved.exists(), 'saved materials URL catalog missing')
        self.assertEqual(json.loads(saved.read_text()), canonical)
        sources = canonical['links']
        self.assertEqual(len({x['id'] for x in sources}), len(sources))
        self.assertTrue(all(x['id'] for x in sources))
        text = index.read_text()
        for item in canonical['links']:
            self.assertIn(item['url'], text)

    def test_portable_reference_is_embedded(self):
        module = load('prompts', ROOT / 'scripts/build_portable_prompts.py')
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root/'skills/example/references').mkdir(parents=True)
            (root/'skills/example/SKILL.md').write_text('---\nname: example\ndescription: example\n---\nRead [rules](references/rules.md).')
            (root/'skills/example/references/rules.md').write_text('Specific canonical rule: keep official logos intact.')
            module.ROOT = root
            result = module.build_prompt({'id':'example','version':'1','portable_references':['rules.md'],'compatibility':{'en':'Images required.'}}, 'en')
            self.assertIn('Specific canonical rule', result)
            self.assertIn('Images required.', result)
            self.assertNotIn('(references/rules.md)', result)

if __name__=='__main__': unittest.main()
