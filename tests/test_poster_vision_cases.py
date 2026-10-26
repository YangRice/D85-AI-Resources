"""Reference preparation regressions; synthetic files, no official artwork."""
import hashlib
import importlib.util
import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('vision_case_builder',ROOT/'tests/build_poster_vision_cases.py')
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class OfficialReferencePreparation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'references').mkdir()
        buffer = io.BytesIO()
        Image.new('RGBA',(40,30),'white').save(buffer,format='PNG')
        self.data = buffer.getvalue()

    def archive(self, members):
        with zipfile.ZipFile(self.root/'logo.zip','w') as archive:
            for member in members:
                archive.writestr(member,self.data)
            # Only explicitly permitted paths should be read.
            archive.writestr('../../unwanted.png',self.data)

    def test_all_permitted_variants_are_prepared_with_inspectable_names(self):
        self.archive(builder.OFFICIAL_LOGO_MEMBERS)
        variants = builder.official_logo_references(self.root,self.root)
        names = [Path(v['path']).name for v in variants]
        self.assertEqual(names,[Path(n).name for n in builder.OFFICIAL_LOGO_MEMBERS])
        self.assertIn('ToastmastersLogo3Color.png',names)
        self.assertEqual(len(list((self.root/'references').iterdir())),4)
        self.assertTrue(all('wordmark_height_ratio' not in v for v in variants))

    def test_missing_variant_fails_instead_of_silently_narrowing_coverage(self):
        self.archive(builder.OFFICIAL_LOGO_MEMBERS[:1])
        with self.assertRaises(KeyError):
            builder.official_logo_references(self.root,self.root)

    def test_precomputed_ratio_is_bound_to_exact_source_revision(self):
        self.archive(builder.OFFICIAL_LOGO_MEMBERS)
        known = {hashlib.sha256(self.data).hexdigest():(7,40)}
        with patch.object(builder,'LOGO_X_MEASUREMENTS',known):
            variants = builder.official_logo_references(self.root,self.root)
        self.assertTrue(all(v['wordmark_height_ratio']==7/40 for v in variants))

    def test_wordmarks_include_every_color_and_measure_tight_source_dimensions(self):
        with zipfile.ZipFile(self.root/'wordmark.zip','w') as archive:
            for member in builder.OFFICIAL_WORDMARK_MEMBERS:
                archive.writestr(member,self.data)
        variants = builder.official_wordmark_references(self.root,self.root)
        self.assertEqual([Path(v['path']).name for v in variants],
                         [Path(n).name for n in builder.OFFICIAL_WORDMARK_MEMBERS])
        self.assertTrue(all(v['wordmark_height_ratio']==30/40 for v in variants))

    def test_real_case_observations_never_collapse_to_a_model_guessed_variant(self):
        import json
        self.archive(builder.OFFICIAL_LOGO_MEMBERS)
        with zipfile.ZipFile(self.root/'wordmark.zip','w') as archive:
            for member in builder.OFFICIAL_WORDMARK_MEMBERS:
                archive.writestr(member,self.data)
        images=[]
        for i in range(3):
            path=self.root/f'poster-{i}.png'
            Image.new('RGB',(720,1280),'#004165').save(path)
            images.append(path)
        samples=builder.real_observations(images,self.root,self.root)
        for index,sample in enumerate(samples):
            observation=json.loads(Path(sample['observations']).read_text())
            logo=observation['logos'][0]
            expected=builder.OFFICIAL_WORDMARK_MEMBERS if index==1 else builder.OFFICIAL_LOGO_MEMBERS
            self.assertNotIn('reference',logo)
            self.assertEqual([Path(v['path']).name for v in logo['references']],
                             [Path(v).name for v in expected])


if __name__ == '__main__':
    unittest.main()
