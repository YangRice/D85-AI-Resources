import importlib.util
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class PosterResources(unittest.TestCase):
    def test_materials_catalog_contains_every_saved_source(self):
        canonical = json.loads((ROOT/'references/toastmasters-brand/asset-sources.json').read_text())
        index = ROOT/'materials/toastmasters-brand/README.md'
        self.assertTrue(index.exists(), 'materials entry point missing')
        saved = ROOT/'materials/toastmasters-brand/sources.json'
        self.assertTrue(saved.exists(), 'saved materials URL catalog missing')
        self.assertEqual(json.loads(saved.read_text()), canonical)
        text = index.read_text()
        for item in canonical['links']:
            self.assertIn(item['url'], text)

    def test_range_reader_enforces_aggregate_budget(self):
        module = load('assets', ROOT/'skills/toastmasters-poster-maker/scripts/fetch_brand_assets.py')
        try:
            reader = module.RangeZip(100, lambda start, count: b'x'*count, max_bytes=10)
        except TypeError:
            self.fail('Range reader has no aggregate byte budget')
        self.assertEqual(reader.read(6), b'x'*6)
        with self.assertRaises(ValueError): reader.read(6)

    def test_remote_zip_reads_only_requested_member(self):
        module = load('assets', ROOT/'skills/toastmasters-poster-maker/scripts/fetch_brand_assets.py')
        self.assertTrue(hasattr(module, 'RangeZip'), 'selective photo-archive access not implemented')
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as archive:
            archive.writestr('photo.jpg', b'photo-data')
            archive.writestr('large-unrelated.bin', b'x' * 1000000)
        data = buf.getvalue()
        requests = []
        def read_range(start, count):
            requests.append((start, count))
            return data[start:start+count]
        with zipfile.ZipFile(module.RangeZip(len(data), read_range)) as archive:
            self.assertEqual(archive.read('photo.jpg'), b'photo-data')
        self.assertLess(sum(count for _, count in requests), 10000)

    def test_standalone_bundles_and_source_ids_are_consistent(self):
        canonical = ROOT/'references/toastmasters-brand'
        sources = json.loads((canonical/'asset-sources.json').read_text())['links']
        self.assertEqual(len({x['id'] for x in sources}), len(sources))
        self.assertTrue(all(x['id'] for x in sources))
        for skill in ('toastmasters-poster-maker', 'toastmasters-poster-reviewer'):
            for source in canonical.glob('*'):
                if source.suffix in {'.md', '.json'}:
                    self.assertEqual((ROOT/'skills'/skill/'references'/source.name).read_bytes(), source.read_bytes())

    def test_generated_poster_prompts_are_standalone_and_current(self):
        module = load('prompts', ROOT/'scripts/build_portable_prompts.py')
        for item in module.CATALOG['skills']:
            if not item['id'].startswith('toastmasters-poster-'):
                continue
            for lang in ('en', 'zh'):
                result = module.build_prompt(item, lang)
                self.assertEqual((ROOT/'prompts'/f"{item['id']}.{lang}.md").read_text(), result)
                self.assertNotIn('(references/', result)
                self.assertEqual(result.count('# Toastmasters poster brand rules' if lang=='en' else '# 头马海报品牌规则'), 1)

    def test_fresh_cache_detects_change_from_bundled_snapshot(self):
        import hashlib
        module = load('assets', ROOT/'skills/toastmasters-poster-maker/scripts/fetch_brand_assets.py')
        with tempfile.TemporaryDirectory() as td:
            baseline = hashlib.sha256(b'old manual').hexdigest()
            try:
                result = module.store_download(Path(td), 'brand-manual', 'https://example.org/manual.pdf', b'new manual', expected_sha256=baseline)
            except TypeError:
                self.fail('fresh caches do not compare against the bundled snapshot')
            self.assertEqual(result['status'], 'changed-review-required')
            self.assertFalse((Path(td)/'brand-manual.json').exists())

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

    def test_changed_asset_preserves_baseline(self):
        path = ROOT/'skills/toastmasters-poster-maker/scripts/fetch_brand_assets.py'
        self.assertTrue(path.exists(), 'asset helper not implemented')
        module = load('assets', path)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = module.store_download(root, 'logo', 'https://example.org/logo.zip', b'first')
            second = module.store_download(root, 'logo', 'https://example.org/logo.zip', b'second')
            self.assertEqual(first['status'], 'downloaded')
            self.assertEqual(second['status'], 'changed-review-required')
            self.assertEqual(Path(first['path']).read_bytes(), b'first')
            self.assertEqual(Path(second['candidate_path']).read_bytes(), b'second')

    def test_archive_inventory_excludes_metadata_and_detects_unsafe_paths(self):
        path=ROOT/'skills/toastmasters-poster-maker/scripts/fetch_brand_assets.py'
        self.assertTrue(path.exists(), 'asset helper not implemented')
        module=load('assets',path)
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w') as z:
            z.writestr('__MACOSX/._logo.png', b'junk')
            z.writestr('logos/.DS_Store', b'junk')
            z.writestr('logos/logo.svg', b'<svg/>')
        self.assertEqual(module.archive_files(buf.getvalue()), ['logos/logo.svg'])
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w') as z: z.writestr('../escape.svg', b'<svg/>')
        with self.assertRaises(ValueError): module.archive_files(buf.getvalue())

if __name__=='__main__': unittest.main()
