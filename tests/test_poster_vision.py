"""Visual route regressions: supplied masks are evidence, not an approval oracle."""
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT/'skills/toastmasters-poster-reviewer/scripts'


def load(name):
    spec = importlib.util.spec_from_file_location('test_'+name,FOLDER/(name+'.py'))
    module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


try:
    import cv2
    import numpy as np
    from PIL import Image
except ImportError:
    cv2 = None


@unittest.skipIf(cv2 is None,'Optional OpenCV, numpy and Pillow required')
class MaskedColorMeasurements(unittest.TestCase):
    def setUp(self):
        self.module = load('color_vision')
        self.rules = json.loads((FOLDER/'brand_rules.json').read_text())
        self.observation = dict(include=[dict(polygon=[[0,0],[200,0],[200,150],[0,150]],reason='design')],exclude=[])

    def test_brand_colors_and_photo_exclusion(self):
        image = Image.new('RGB',(200,150),'#004165')
        image.paste('#FF00FF',(80,40,150,110))
        self.observation['exclude']=[dict(polygon=[[78,38],[152,38],[152,112],[78,112]],reason='photo',kind='photo')]
        result = self.module.inspect_colors(image,self.observation,self.rules)
        self.assertEqual(result['status'],'PASS',result)
        self.assertGreater(result['mask_counts']['excluded'],0)
        self.assertIn('not independently verified',result['mask_basis'])

    def test_large_wrong_color_and_small_wrong_patch_survive_clustering(self):
        for bounds in ((0,0,200,150),(95,65,107,77)):
            image = Image.new('RGB',(200,150),'#004165');image.paste('#FF00FF',bounds)
            self.observation['requested_k']=1
            result=self.module.inspect_colors(image,self.observation,self.rules)
            self.assertEqual(result['status'],'REVISE',result)
            self.assertGreater(result['material_off_palette_pixels'],0)

    def test_permitted_gradient_intermediates_and_neutrals(self):
        image = Image.new('RGB',(200,150))
        for x in range(200):
            value=(0,round(65+31*x/199),round(101+47*x/199))
            image.paste(value,(x,0,x+1,150))
        image.paste('white',(0,100,100,150));image.paste('black',(100,100,200,150))
        result=self.module.inspect_colors(image,self.observation,self.rules)
        self.assertEqual(result['status'],'PASS',result)
        again=self.module.inspect_colors(image,self.observation,self.rules)
        self.assertEqual(result,again)

    def test_empty_excluded_all_and_outside_masks_do_not_pass(self):
        image=Image.new('RGB',(200,150),'#004165')
        self.assertEqual(self.module.inspect_colors(image,dict(include=[],exclude=[]),self.rules)['status'],'BLOCKED')
        self.observation['exclude']=self.observation['include']
        self.assertEqual(self.module.inspect_colors(image,self.observation,self.rules)['status'],'BLOCKED')
        with self.assertRaises(ValueError):
            self.module.polygon_mask(image.size,[dict(polygon=[[0,0],[500,0],[0,100]],reason='bad')])


@unittest.skipIf(cv2 is None,'Optional OpenCV, numpy and Pillow required')
class VisualRoute(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.image=self.root/'poster.png'
        Image.new('RGB',(200,150),'#004165').save(self.image)
        self.module=load('check_brand');self.spec=load('vision_review').template()
        self.spec.update(candidate_sha256=hashlib.sha256(self.image.read_bytes()).hexdigest(),
            requested_checks=['design_palette'], colors=dict(include=[dict(
                polygon=[[0,0],[200,0],[200,150],[0,150]],reason='model selected background')],exclude=[]))

    def test_new_scope_does_not_require_source_inventory_or_call_ocr(self):
        with patch('subprocess.run',side_effect=AssertionError('OCR must not run')):
            result=self.module.inspect(self.image,self.spec,self.root)
        self.assertEqual(result['scoped_verdict'],'PASS')
        self.assertNotIn('full_brand_verdict',result)
        self.assertNotIn('visual_brand_verdict',result)

    def test_wrong_candidate_invalid_checks_and_duplicate_entities_rejected(self):
        self.spec['candidate_sha256']='wrong'
        with self.assertRaises(ValueError):self.module.inspect(self.image,self.spec,self.root)
        self.spec['candidate_sha256']=hashlib.sha256(self.image.read_bytes()).hexdigest()
        self.spec['requested_checks']=[]
        with self.assertRaises(ValueError):self.module.inspect(self.image,self.spec,self.root)
        self.spec['requested_checks']=['logo_detection'];self.spec['logos']=[dict(id='same'),dict(id='same')]
        with self.assertRaises(ValueError):self.module.inspect(self.image,self.spec,self.root)

    def test_model_copy_can_revise_without_font_files_or_ocr(self):
        self.spec.update(requested_checks=['tagline','marketing_phrases'],
            text_runs=[dict(text='WHERE LEADERS ARE LOST',role='tagline',readability='clear')],
            text_inventory_complete=False)
        with patch('subprocess.run',side_effect=AssertionError('OCR must not run')):
            result=self.module.inspect(self.image,self.spec,self.root)
        self.assertEqual(result['feature_results']['tagline']['status'],'REVISE')
        self.assertEqual(result['feature_results']['marketing_phrases']['status'],'BLOCKED')
        self.assertEqual(result['scoped_verdict'],'REVISE')
        self.assertIn('model observation',result['findings'][0]['evidence_type'])

    def test_ambiguous_text_and_empty_inventory_never_confirm_copy(self):
        self.spec.update(requested_checks=['tagline','marketing_phrases'],
            text_runs=[dict(text='WHERE LEADERS ARE MADE',role='tagline',readability='uncertain')])
        result=self.module.inspect(self.image,self.spec,self.root)
        self.assertTrue(all(v['status']=='BLOCKED' for v in result['feature_results'].values()))

    def test_observations_cli(self):
        path=self.root/'observations.json';path.write_text(json.dumps(self.spec))
        result=subprocess.run([sys.executable,str(FOLDER/'check_brand.py'),'--candidate',str(self.image),
                               '--observations',str(path)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(json.loads(result.stdout)['scoped_verdict'],'PASS')

    def test_exported_template_runs_through_the_only_cli_input(self):
        exported = subprocess.run([sys.executable, str(FOLDER/'check_brand.py'), '--template'],
                                  capture_output=True, text=True)
        self.assertEqual(exported.returncode, 0, exported.stdout + exported.stderr)
        observation = json.loads(exported.stdout)
        # Keep the exported format/rule identifier, then supply actual observations.
        observation.update(candidate_sha256=self.spec['candidate_sha256'],
                           requested_checks=['design_palette'], colors=self.spec['colors'])
        path = self.root/'from-template.json'
        path.write_text(json.dumps(observation))
        result = subprocess.run([sys.executable, str(FOLDER/'check_brand.py'),
                                 '--candidate', str(self.image), '--observations', str(path)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['scoped_verdict'], 'PASS')

    def test_invalid_exports_are_rejected_before_measurement(self):
        transparent = self.root/'transparent.png'
        Image.new('RGBA', (30, 30), (0, 65, 101, 0)).save(transparent)
        animation = self.root/'poster.gif'
        Image.new('RGB', (30, 30), '#004165').save(animation)
        for candidate in (transparent, animation):
            with self.subTest(candidate=candidate.name), self.assertRaises(ValueError):
                self.module.inspect(candidate, self.spec, self.root)

    def test_missing_cv_dependency_does_not_fabricate_measurements(self):
        with patch.dict(sys.modules,{'cv2':None}):
            with self.assertRaises(ImportError):
                self.module.inspect(self.image,self.spec,self.root)

    def test_unmeasured_effects_are_not_an_empty_scoped_pass(self):
        import types
        source=self.root/'reference.png';Image.new('RGBA',(40,30),'white').save(source)
        spec=dict(self.spec,requested_checks=['logo_effects'],logos=[dict(id='one',reference=str(source))])
        route=load('vision_review')
        detector=types.SimpleNamespace(inspect_logo=lambda *a:dict(
            detection=dict(status='PASS'),effects=dict(status='INFO',reason='Textured background needs review')))
        with patch.object(route,'load_module',return_value=detector):
            with Image.open(self.image) as opened:
                result=route.inspect(opened,spec,self.root,self.image)
        self.assertEqual(result['scoped_verdict'],'BLOCKED')
        self.assertEqual(result['logo_measurements'][0]['selected']['effects']['status'],'INFO')

    def test_variant_measurements_do_not_inherit_another_source_ratio(self):
        import types
        source=self.root/'reference.png';Image.new('RGBA',(40,30),'white').save(source)
        route=load('vision_review')
        seen=[]
        def measure(image, reference, params):
            seen.append(params.get('wordmark_height_ratio'))
            return dict(detection=dict(status='PASS'),appearance=dict(status='PASS',mean_delta_e76=1))
        detector=types.SimpleNamespace(inspect_logo=measure)
        self.spec.update(requested_checks=['logo_detection'],logos=[dict(id='one',
            wordmark_height_ratio=.9,references=[
                dict(path=str(source),wordmark_height_ratio=.2),dict(path=str(source))])])
        with patch.object(route,'load_module',return_value=detector):
            with Image.open(self.image) as opened:
                result=route.inspect(opened,self.spec,self.root,self.image)
        self.assertEqual(seen,[.2,None])
        hypotheses=result['logo_measurements'][0]['hypotheses']
        self.assertEqual(hypotheses[0]['wordmark_height_ratio'],.2)
        self.assertIsNone(hypotheses[1]['wordmark_height_ratio'])
        self.spec['logos'][0]['references']=[dict(path=str(source),unexpected=True)]
        with Image.open(self.image) as opened:
            with self.assertRaisesRegex(ValueError,'Unknown reference variant fields'):
                route.inspect(opened,self.spec,self.root,self.image)

    def test_sparse_variant_cannot_win_only_by_comparing_fewer_pixels(self):
        import types
        route=load('vision_review')
        sources=[]
        for name in ('sparse.png','full.png'):
            path=self.root/name
            Image.new('RGBA',(40,30),'white').save(path)
            sources.append(str(path))
        self.spec.update(requested_checks=['logo_appearance'],
            logos=[dict(id='one',references=sources)])
        calls=[]
        def measure(*args):
            sparse=not calls
            calls.append(True)
            return dict(detection=dict(status='PASS',method='SIFT + RANSAC homography'),
                appearance=dict(status='PASS',mean_delta_e76=2 if sparse else 9),
                diagnostics=dict(attempts=[dict(inliers=40 if sparse else 100,
                                               reference_hull_fraction=.3 if sparse else .6)]))
        with patch.object(route,'load_module',return_value=types.SimpleNamespace(inspect_logo=measure)):
            with Image.open(self.image) as opened:
                result=route.inspect(opened,self.spec,self.root,self.image)
        selected=result['logo_measurements'][0]['selected']
        self.assertEqual(selected['reference_name'],'full.png')
        self.assertEqual(selected['variant_match_support'],60)


if __name__=='__main__':unittest.main()
